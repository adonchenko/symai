# Use an official Python runtime as a parent image
FROM python:3.12-slim
#voumes
VOLUME /app/properties
VOLUME /app/logdir
# Set the working directory in the container
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY ./expression.py /app/expression.py
COPY ./symaiconfig.py /app/symaiconfig.py
# Install any needed dependencies specified in requirements.txt
RUN pip3 install sympy
#RUN pip install --no-cache-dir -r requirements.txt
# Make port 8080 available to the world outside this container
EXPOSE 8080
# Run app.py when the container launches
CMD ["python", "expression.py"]
