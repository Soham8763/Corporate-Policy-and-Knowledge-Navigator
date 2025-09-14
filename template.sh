touch .env
touch .gitignore
touch README.md
touch requirements.txt
touch main.py
touch streamlit_app.py
touch process_documents.py

# Creating the data directory and subdirectories
mkdir -p data/documents
mkdir -p data/samples

# Creating sample documents for testing
touch data/samples/employee_handbook.pdf
touch data/samples/travel_policy.pdf
touch data/samples/it_security_policy.pdf

# Creating the chroma directory (for the vector store)
mkdir -p chroma

# Creating the utils directory and its files
mkdir -p utils
touch utils/__init__.py
touch utils/file_handlers.py
touch utils/citation_formatter.py
touch utils/auth_service.py

# Creating the config directory and its files
mkdir -p config
mkdir -p config/prompts
touch config/roles.json
touch config/prompts/base_prompt.txt
touch config/prompts/hr_role_prompt.txt
touch config/prompts/it_admin_prompt.txt

# Creating the tests directory and its files
mkdir -p tests
touch tests/test_api.py
touch tests/test_document_processing.py

echo "File and folder structure created successfully as per the provided tree."