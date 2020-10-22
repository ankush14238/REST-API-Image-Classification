FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python3 -m pip install --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-0.12.0-py3-none-any.whl
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "app.py" ]