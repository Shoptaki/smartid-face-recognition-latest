
## Facial Recognition code

This is a official facial recognition repo of shoptaki.


## Tech Stack

**Server:** Python, FastAPI, websocket

**Database:**  arangodb, minio

**Model:** mediapipe, facial_recognition


## Folder structure
```bash
shoptaki-smartid
|_src
  |_core/detection
    |_video_capture.py
    |_liveliness_detection.py
    |_guided_liveliness.py
  |_data
    |_database.py
  |_routes
    |_example_routes.py
    |_sample.html
  |_ main.py
  |_environment
```

| File      | Description                |
| :-------- | :------------------------- |
| `video_capture.py` | file with the facial recognition logic |
| `liveliness_detection.py` | liveliness detection |
| `guided_liveliness.py` | guided liveliness detection|
| `database.py` | to interact with database|
| `example_routes.py` | routes to the endpoints|
| `main.py` | fastAPI main server file|

## Run Locally
- Install and run Minio: follow the instructions [here](https://min.io/docs/minio/macos/index.html)
- Fire up the docker engine and follow the instructions [here](https://hub.docker.com/_/arangodb) for arangodb.
- once pulled, run the image and update the minIO and arangodb credentials in database.py. We are using pyarango as database driver. checkout documentation for that [here](https://docs.python-arango.com/en/main/)

Clone the project

```bash
  git clone https://github.com/Shoptaki/shoptaki-smartid.git
```

Go to the project directory

```bash
  cd shoptaki-smartid
```

Make python virtual environment by running this command

```bash
  cd src && source environment/bin/activate
```

Install all the dependencies

```bash
  pip3 install -r requirements.txt
```

Start the server
```bash
  uvicorn main:app --host 0.0.0.0 --port 8080 --reload 
```
change the arangodb and minio config in the `database.py`

You can see the API running at https://localhost:8000

./minio server ~/minio/data

Few key points

    1. The code is not yet dockerized. will be done soon enough
    2. requirements: running arangodb and minio.

Few key points

    1. The code is not yet dockerized. will be done soon enough
    2. requirements : running arangodb and minio.


