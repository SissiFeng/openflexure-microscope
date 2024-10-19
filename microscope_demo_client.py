import base64
import io
import json
import os
import shutil
import time
import asyncio
from io import BytesIO
from typing import List, Dict, Union, Optional
import logging

from mqtt_client import MQTTClient
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MicroscopeDemo:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        microscope: str,
        path_to_openflexure_stitching: str = "OPTIONAL",
    ):
        """
        Initialize the MicroscopeDemo client.

        Args:
            host (str): MQTT broker host.
            port (int): MQTT broker port.
            username (str): MQTT username.
            password (str): MQTT password.
            microscope (str): Microscope identifier.
            path_to_openflexure_stitching (str, optional): Path to OpenFlexure stitching software.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.microscope = microscope
        self.path_to_openflexure_stitching = path_to_openflexure_stitching

        self.client = MQTTClient(host, port, f"microscope-demo-{microscope}", username, password)

        self.receiveq = asyncio.Queue()

        def on_message(client, userdata, message):
            received = json.loads(message.payload.decode("utf-8"))
            asyncio.create_task(self.receiveq.put(received))
            logger.debug(f"Received message: {received}")

        self.client.client.on_message = on_message

        try:
            self.client.connect()
            logger.info("Connected to MQTT broker")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

        self.client.subscribe(self.microscope + "/return", qos=2)

    async def scan_and_stitch(
        self, 
        c1: Union[str, List[int]], 
        c2: Union[str, List[int]], 
        temp: str, 
        ov: int = 1200, 
        foc: int = 0, 
        output: str = "Downloads/stitched.jpeg"
    ) -> None:
        """
        Scan an area and stitch the resulting images.

        Args:
            c1 (Union[str, List[int]]): First corner coordinates.
            c2 (Union[str, List[int]]): Second corner coordinates.
            temp (str): Temporary directory for storing images.
            ov (int, optional): Overlap between images. Defaults to 1200.
            foc (int, optional): Focus adjustment between images. Defaults to 0.
            output (str, optional): Output path for stitched image. Defaults to "Downloads/stitched.jpeg".
        """
        command = json.dumps(
            {"command": "scan", "c1": c1, "c2": c2, "ov": ov, "foc": foc}
        )
        self.client.publish(
            self.microscope + "/command", command, qos=2
        )
        image = await self.receiveq.get()
        image_list = image["images"]
        if os.path.isdir(temp):
            shutil.rmtree(temp)
        os.makedirs(temp)
        for i, img_data in enumerate(image_list):
            image_bytes = base64.b64decode(img_data)
            with io.BytesIO(image_bytes) as buffer:
                img = Image.open(buffer)
                img.save(
                    os.path.join(temp, f"{i}.jpeg"),
                    format="JPEG",
                    exif=img.info.get("exif"),
                )
        
        # Run OpenFlexure stitching
        stitch_command = (
            f"cd {self.path_to_openflexure_stitching} && "
            "python -m venv .venv && "
            ".\.venv\Scripts\activate && "
            f"openflexure-stitch {temp}"
        )
        os.system(stitch_command)

        # Move stitched image to output location
        stitched_file = f"{os.path.basename(temp)}_stitched.jpg"
        shutil.move(os.path.join(temp, stitched_file), output)

    async def move(self, x: int, y: int, z: Optional[int] = None, relative: bool = False) -> Dict:
        """
        Move the microscope to specified coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            z (Optional[int], optional): Z coordinate. If None, Z won't change. Defaults to None.
            relative (bool, optional): If True, move relative to current position. Defaults to False.

        Returns:
            Dict: Response from the microscope.
        """
        command = json.dumps(
            {"command": "move", "x": x, "y": y, "z": z, "relative": relative}
        )
        self.client.publish(
            self.microscope + "/command", command, qos=2
        )
        return await self.receiveq.get()

    async def scan(self, c1: Union[str, List[int]], c2: Union[str, List[int]], ov: int = 1200, foc: int = 0) -> List[Image.Image]:
        """
        Scan an area and return a list of images.

        Args:
            c1 (Union[str, List[int]]): First corner coordinates.
            c2 (Union[str, List[int]]): Second corner coordinates.
            ov (int, optional): Overlap between images. Defaults to 1200.
            foc (int, optional): Focus adjustment between images. Defaults to 0.

        Returns:
            List[Image.Image]: List of scanned images.
        """
        command = json.dumps(
            {"command": "scan", "c1": c1, "c2": c2, "ov": ov, "foc": foc}
        )
        self.client.publish(
            self.microscope + "/command", command, qos=2
        )
        image_l = await self.receiveq.get()
        return [Image.open(BytesIO(base64.b64decode(img))) for img in image_l["images"]]

    async def focus(self, amount: Union[str, int] = "fast") -> Dict:
        """
        Focus the microscope.

        Args:
            amount (Union[str, int], optional): Focus amount. Can be "huge", "fast", "medium", "fine", or an integer. Defaults to "fast".

        Returns:
            Dict: Response from the microscope.
        """
        command = json.dumps({"command": "focus", "amount": amount})
        self.client.publish(
            self.microscope + "/command", command, qos=2
        )
        return await self.receiveq.get()

    async def get_pos(self) -> Dict[str, int]:
        """
        Get the current position of the microscope.

        Returns:
            Dict[str, int]: Dictionary with x, y, and z coordinates.
        """
        command = json.dumps({"command": "get_pos"})
        self.client.publish(
            self.microscope + "/command", command, qos=2
        )
        pos = await self.receiveq.get()
        return pos["pos"]

    async def take_image(self) -> Image.Image:
        """
        Take an image with the microscope.

        Returns:
            Image.Image: Captured image.
        """
        command = json.dumps({"command": "take_image"})
        self.client.publish(
            self.microscope + "/command", command, qos=2
        )
        image = await self.receiveq.get()
        image_bytes = base64.b64decode(image["image"])
        return Image.open(BytesIO(image_bytes))

    def end_connection(self):
        """End the connection to the microscope."""
        self.client.disconnect()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end_connection()

# Example usage
async def main():
    async with MicroscopeDemo("f84673212a5c46da8fa64f37d38b3630.s1.eu.hivemq.cloud", 8883, "username", "password", "microscope1") as microscope:
        image = await microscope.take_image()
        image.save("captured_image.jpg")
        
        position = await microscope.get_pos()
        print(f"Current position: {position}")

if __name__ == "__main__":
    asyncio.run(main())
