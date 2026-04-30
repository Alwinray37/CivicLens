import json

class JsonHelper:
    @staticmethod
    def load_json_data(json_filename):
        """
        Loads JSON data from a file.

        Args:
            json_filename (str): Path to the JSON file.

        Returns:
            dict or None: Parsed JSON data if successful, None otherwise.
        """
        try:
            with open(json_filename, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"Error: '{json_filename}' not found")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{json_filename}'")
        # Return None if file not found or JSON is invalid
        return None
    
    @staticmethod
    def write_json_data(json_filename, data):
        """
        Writes JSON data to a file.

        Args:
            json_filename (str): Path to the JSON file.
            data (dict): Data to write to the file.
        """
        with open(json_filename, 'w') as file:
            json.dump(data, file, indent=4)