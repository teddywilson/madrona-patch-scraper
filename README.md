# madrona-patch-scraper

Basic script to scrape Madrona Labs forums and pull community patches into a local library.

## Usage
```
pip3 install -r requirements.txt
python scraper.py --output_dir=/Path/to/your/directory
```

## TODO 
- [ ] Diffing between runs (or just checking if filename already exists)
- [ ] Linking to Madrona discovery folder (maybe)
- [x] Parse all patch types (namely adding json support)
- [x] `html_patch_#` -> useful filename
