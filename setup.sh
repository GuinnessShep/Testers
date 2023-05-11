#!/bin/bash

echo "Installing dependencies..."
pkg install python clang wget -y

echo "Installing APKTool..."
wget https://github.com/iBotPeaches/Apktool/releases/download/v2.5.2/apktool_2.5.2_all.deb
dpkg -i apktool_2.5.2_all.deb

echo "Installing JDK..."
pkg install openjdk-17 -y

echo "Setting up environment variables..."
echo "export JAVA_HOME=/data/data/com.termux/files/usr/libexec/openjdk-17" >> $HOME/.bashrc
echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> $HOME/.bashrc
source $HOME/.bashrc

echo "Installing Python packages..."
pip install frida-tools cryptography

echo "Setup complete!"
