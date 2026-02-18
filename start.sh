# Setting the base directory where everything gets cloned into (helps agains permission issues on USB drive)
BASE_DIR="/bin/BotBall_Library"

# Create directory
mkdir $BASE_DIR

# Clone everything from the Library to the base directory
cp -R ./ $BASE_DIR

# Set permissions of the base directory and every file + folder in it
chmod 777 -R $BASE_DIR

# Execute the configurations
bash $BASE_DIR/src/scripts/config.sh