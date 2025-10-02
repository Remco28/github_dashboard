# Docker Deployment Guide for WSL Ubuntu

This guide will walk you through installing Docker on WSL Ubuntu, containerizing your Python application, and running it as a Docker container.

## Part 1: Installing Docker on WSL Ubuntu

These steps will guide you through the installation of Docker on your WSL Ubuntu environment.

### Step 1: Update your package manager

First, we'll update the package list to ensure we have the latest information about available packages.

```bash
sudo apt-get update
```

### Step 2: Install prerequisite packages

These packages are required to allow `apt` to use a repository over HTTPS.

```bash
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

### Step 3: Add Docker's official GPG key

This step adds Docker's official GPG key to your system, which ensures that the Docker packages you install are authentic.

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

### Step 4: Set up the Docker repository

This command sets up the `apt` repository to point to the stable version of Docker for your Ubuntu distribution.

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Step 5: Install Docker Engine

Now, we'll install the Docker Engine, which includes the Docker daemon, the client, and other tools.

```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Step 6: Verify Docker installation

You can verify that Docker is installed correctly by running the `hello-world` image.

```bash
sudo docker run hello-world
```

You should see a message indicating that your installation appears to be working correctly.

### Step 7: Run Docker without `sudo` (Optional but recommended)

To avoid typing `sudo` every time you run a Docker command, you can add your user to the `docker` group.

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

You will need to **log out and log back in** for this to take effect. You can also run `newgrp docker` to apply the new group membership immediately in your current shell.

## Part 2: Preparing your project for containerization

Now that Docker is installed, we need to tell Docker how to build and run your application.

### Step 1: Create a `.dockerignore` file

This file tells Docker which files and directories to ignore when building the image. This is important to keep your image small and to avoid sending sensitive information to the Docker daemon.

Create a file named `.dockerignore` in your project root with the following content:

```
# Ignore virtual environment
github_dashboard_env/

# Ignore git repository
.git/

# Ignore python cache
__pycache__/
*.pyc

# Ignore other artifacts
.devcontainer/
.gitignore
*.md
```

### Step 2: Understand the `Dockerfile`

The `Dockerfile` is a text document that contains all the commands a user could call on the command line to assemble an image.

Here is a `Dockerfile` for your project. I see you already have one, but this one is tailored to a production environment.

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code from your host to your image filesystem.
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]
```

**Explanation of the `Dockerfile`:**

* `FROM python:3.9-slim`: This specifies the base image for our container. `python:3.9-slim` is a lightweight version of the Python 3.9 image.
* `WORKDIR /app`: This sets the working directory inside the container to `/app`. All subsequent commands will be run from this directory.
* `COPY requirements.txt .`: This copies the `requirements.txt` file from your local project directory into the `/app` directory in the container.
* `RUN pip install --no-cache-dir -r requirements.txt`: This installs the Python dependencies defined in `requirements.txt`. The `--no-cache-dir` option is used to keep the image size small.
* `COPY . .`: This copies the rest of your application's code into the `/app` directory in the container.
* `EXPOSE 8501`: This informs Docker that the container listens on port 8501 at runtime. This is the default port for Streamlit applications.
* `CMD ["streamlit", "run", "app.py"]`: This specifies the command to run when the container starts. It will execute `streamlit run app.py`.

## Part 3: Building and Running the Docker Container

Now we can build the image and run the container.

### Step 1: Build the Docker image

This command will build a Docker image from your `Dockerfile`. The `-t` flag tags the image with a name, which makes it easier to refer to later.

```bash
docker build -t github-dashboard .
```

The `.` at the end of the command tells Docker to use the current directory as the build context.

### Step 2: Run the Docker container

This command will run the Docker container from the image we just built.

```bash
docker run -p 8501:8501 github-dashboard
```

**Explanation of the `docker run` command:**

* `-p 8501:8501`: This maps port 8501 on your local machine to port 8501 in the container. This allows you to access the Streamlit application by navigating to `http://localhost:8501` in your web browser.
* `github-dashboard`: This is the name of the image we want to run.

You should now be able to access your application at `http://localhost:8501`.

## Part 4: Managing your container

Here are some useful commands for managing your Docker containers.

* **List running containers:**
  
  ```bash
  docker ps
  ```
* **List all containers (including stopped ones):**
  
  ```bash
  docker ps -a
  ```
* **Stop a container:**
  
  ```bash
  docker stop <container_id_or_name>
  ```
* **View the logs of a container:**
  
  ```bash
  docker logs <container_id_or_name>
  ```
* **Remove a stopped container:**
  
  ```bash
  docker rm <container_id_or_name>
  ```
* **List Docker images:**
  
  ```bash
  docker images
  ```
* **Remove a Docker image:**
  
  ```bash
  docker rmi <image_id_or_name>
  ```

This guide should provide a solid foundation for deploying your application with Docker. Let me know if you have any questions!
