import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This should be replaced with a secure database in a production environment
temp_keys = {}

def generate_temp_key(device_id, duration=1800):  # Default duration: 30 minutes
    key = f"temp_{device_id}_{int(time.time())}"
    expiration = time.time() + duration
    temp_keys[key] = {"device_id": device_id, "expiration": expiration}
    return key

def validate_key(key):
    if key in temp_keys:
        if time.time() < temp_keys[key]["expiration"]:
            return temp_keys[key]["device_id"]
        else:
            del temp_keys[key]
            logger.info(f"Key {key} has expired and been removed")
    return None

def check_access(key, device_id):
    valid_device = validate_key(key)
    if valid_device == device_id:
        return True
    return False

# Example usage
if __name__ == "__main__":
    # Generate a temporary key
    device_id = "microscope1"
    temp_key = generate_temp_key(device_id)
    print(f"Generated temporary key: {temp_key}")

    # Check access (should be True)
    print(f"Access granted: {check_access(temp_key, device_id)}")

    # Check access with wrong device (should be False)
    print(f"Access granted: {check_access(temp_key, 'microscope2')}")

    # Wait for key to expire (for testing purposes)
    time.sleep(5)
    temp_keys[temp_key]["expiration"] = time.time() - 1

    # Check access after expiration (should be False)
    print(f"Access granted after expiration: {check_access(temp_key, device_id)}")