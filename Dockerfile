# pull official base image
FROM python:3.6

# set work directory
RUN mkdir -p /docker/neo4jd3
WORKDIR /docker/neo4jd3

# copy project
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# define the default command to run when starting the container
CMD ["gunicorn", "--bind", ":5001", "Neo4jD3_main:app"]
