echo "Updating your system"
apt-get update
echo "installing git"
apt-get install git
echo "installing rust"
apt-get install rust
echo "installing python3"
apt-get install python
echo "installing pip"
apt-get install python-pip
echo "Updating your Burpdroid (beta-version)"
git clone https://github.com/burpdroid/burpdroid-proxy /data/data/com.termux/files/usr/var/burpdroid-proxy
echo "setting env veriable"
export CRYPTOGRAPHY_DONT_BUILD_RUST=1
echo "installing requirement"
pip install -r /data/data/com.termux/files/usr/var/burpdroid-proxy/requirement.txt
echo "python3 /data/data/com.termux/files/usr/var/burpdroid-proxy/main.py" > /data/data/com.termux/files/usr/bin/burpdroid
chmod +x /data/data/com.termux/files/usr/bin/burpdroid
echo "Burpdroid installed successfully"