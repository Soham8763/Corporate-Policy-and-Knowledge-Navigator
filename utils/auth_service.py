import json
import os

def get_allowed_documents(user_role: str, roles_config_path='config/roles.json'):
    """
    Loads role-based access configurations and returns a list of allowed documents.
    """
    try:
        with open(roles_config_path, 'r') as f:
            roles_data = json.load(f)

        return roles_data.get(user_role, [])
    except FileNotFoundError:
        print(f"Warning: Roles configuration file not found at {roles_config_path}. No access restrictions will be applied.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {roles_config_path}.")
        return []

def filter_documents_by_role(documents, allowed_docs):
    """
    Filters a list of documents based on a list of allowed filenames.
    This function is a placeholder for a more robust access control system.
    """
    if not allowed_docs:
        return documents # No restrictions, return all documents

    return [doc for doc in documents if os.path.basename(doc.metadata.get('source')) in allowed_docs]