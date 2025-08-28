# New Main Branch
conda create -n tfve python=3.12
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt

# for visualization
pip install matplotlib
pip install seaborn
pip install opencv-python