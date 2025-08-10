# Flask Image Upload Example with CShelve

This example demonstrates how to use [CShelve](https://github.com/Standard-Cloud/cshelve) as a backend for storing uploaded images in a Flask web application.

## Features
- Upload images via a simple web interface using [Flask](https://flask.palletsprojects.com/en/stable/quickstart/#).
- Store uploaded images with CShelve, seamlessly switching between in-memory storage for development and [Azure](https://standard-cloud.github.io/cshelve/azure-blob/)/[AWS](https://standard-cloud.github.io/cshelve/aws-s3/) cloud backends for production — no changes to application code required.
- Display uploaded images.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Flask app:
    ```bash
    python app.py
    ```
    Or, to use a specific storage provider, run:
    ```bash
    python app.py <provider>.ini
    ```
    Replace `<provider>` with "aws" or "azure", and make sure to set the appropriate credentials.
3. Open [http://localhost:5000](http://localhost:5000) in your browser.

## Two Approaches in This Example

This project demonstrates two ways to integrate CShelve with Flask:

### 1. Using `app-single-access.py`
In this approach, the CShelve database is opened and closed for each request. This ensures that the database is only accessed when needed, making it simple and efficient for most use cases.

### 2. Using `app-shared-access.py`
In this approach, the CShelve database is opened once and shared across requests. This is possible because CShelve supports multi-concurrency, allowing multiple threads or processes to safely access the database simultaneously. This approach can improve performance in high-concurrency scenarios.

To run the desired version:
- For `app-single-access.py`:
  ```bash
  python app.py
  ```
- For `app-shared-access.py`:
  ```bash
  python app-shared-access.py
  ```

Both approaches are valid, and you can choose the one that best fits your application's needs.
