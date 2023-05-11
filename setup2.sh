#!/bin/bash

# Function to check if a command is available
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if frida-core devkit is installed
if ! command_exists frida-deps-14.2.18.tar.xz; then
    echo "Frida core devkit not found. Downloading and installing..."

    # Download frida-core devkit
    wget https://github.com/frida/frida/releases/download/14.2.18/frida-deps-14.2.18.tar.xz

    # Extract devkit
    tar -xf frida-deps-14.2.18.tar.xz

    # Set environment variable
    export FRIDA_CORE_DEVKIT=$(pwd)/frida-deps-14.2.18

    echo "Frida core devkit installed."
else
    echo "Frida core devkit found."
    export FRIDA_CORE_DEVKIT=$(pwd)/frida-deps-14.2.18
fi

# Install dependencies
echo "Installing dependencies..."
apt update
apt install -y python3 python3-pip clang wget openjdk-17

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install APKTool
echo "Installing APKTool..."
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /data/data/com.termux/files/usr/bin/apktool
chmod +x /data/data/com.termux/files/usr/bin/apktool

wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.6.0.jar -O /data/data/com.termux/files/home/apktool.jar

# Set up environment variables
echo "Setting up environment variables..."
echo "export PATH=\$PATH:/data/data/com.termux/files/usr/bin" >> ~/.bashrc
echo "export CLASSPATH=\$CLASSPATH:/data/data/com.termux/files/home/apktool.jar" >> ~/.bashrc
echo "export FRIDA_CORE_DEVKIT=$FRIDA_CORE_DEVKIT" >> ~/.bashrc
source ~/.bashrc

# Install frida from source
echo "Installing frida from source..."
pip3 install cython
pip3 install frida==14.2.18

#!/bin/bash

# Add required APT sources
echo "Adding required APT sources..."
echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list
echo "deb-src http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list.d/bullseye.list
apt update

# Install dependencies
echo "Installing dependencies..."
apt install -y build-essential python3 python3-pip wget default-jdk git

# Install frida from source
echo "Installing frida from source..."
apt install -y automake autoconf libtool pkg-config
git clone https://github.com/frida/frida.git
cd frida
make
make install
cd ..
rm -rf frida

# Install APKTool
echo "Installing APKTool..."
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool
chmod +x /usr/local/bin/apktool
wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.6.0.jar -O /usr/local/bin/apktool.jar

# Install frida-tools from source
echo "Installing frida-tools from source..."
git clone https://github.com/frida/frida-tools.git
cd frida-tools
pip3 install .
cd ..
rm -rf frida-tools

echo "Setup complete."


