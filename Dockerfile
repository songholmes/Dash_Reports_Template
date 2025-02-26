FROM python:3.9-slim

WORKDIR /FoodLens

COPY . /FoodLens

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3002

CMD ["gunicorn", "--bind", "0.0.0.0:3002", "index:server"]
