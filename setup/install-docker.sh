#!/bin/bash

# Turtle Monitoring System - Docker Installation
# Install latest Docker Engine on Ubuntu Server

set -e

echo "📦 Installing Docker Engine..."

# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index with new repository
sudo apt update

# Install Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Enable Docker to start on boot
sudo systemctl enable docker
sudo systemctl start docker

# Test Docker installation
echo "🧪 Testing Docker installation..."
sudo docker run hello-world

echo "✅ Docker installed successfully!"
echo "   Version: $(docker --version)"

# Note about group membership
echo ""
echo "📝 Note: You've been added to the docker group."
echo "   You may need to log out and back in, or run:"
echo "   newgrp docker"
echo ""