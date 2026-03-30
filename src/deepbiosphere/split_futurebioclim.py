import os
import sys
import rasterio


def split_multiband_tif(input_tif, output_dir):
    """
    Split a multi-band GeoTIFF into single-band GeoTIFFs.

    Output naming rule:
        original_filename_without_extension + _{band_number}.tif

    Example:
        wc2.1_30s_bioc_BCC-CSM2-MR_ssp126_2041-2060.tif
        →
        wc2.1_30s_bioc_BCC-CSM2-MR_ssp126_2041-2060_1.tif
        ...
        wc2.1_30s_bioc_BCC-CSM2-MR_ssp126_2041-2060_19.tif
    """

    if not os.path.exists(input_tif):
        raise FileNotFoundError(f"Input file not found: {input_tif}")

    os.makedirs(output_dir, exist_ok=True)

    with rasterio.open(input_tif) as src:
        band_count = src.count
        print(f"Detected {band_count} bands.")

        if band_count != 19:
            print("⚠ Warning: Expected 19 bands (WorldClim bioclim), but found:", band_count)

        base_name = os.path.splitext(os.path.basename(input_tif))[0]

        profile = src.profile.copy()
        profile.update(count=1)  # single band output

        for band in range(1, band_count + 1):
            output_filename = f"{base_name}_{band}.tif"
            output_path = os.path.join(output_dir, output_filename)

            data = src.read(band)

            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(data, 1)

                # Preserve band description if available
                if src.descriptions and src.descriptions[band - 1]:
                    dst.set_band_description(1, src.descriptions[band - 1])

            print(f"Saved: {output_filename}")

    print("✓ Finished splitting.")

if __name__ == "__main__":
    """
    Run from terminal like:

    python split_futurebioclim.py input.tif output_folder

    Example:
    python split_bioclim_bands.py wc2.1_30s_bioc_BCC-CSM2-MR_ssp126_2041-2060.tif ./output
    """

    if len(sys.argv) != 3:
        print("Usage:")
        print("python split_bioclim_bands.py <input_tif> <output_directory>")
        sys.exit(1)

    input_tif = sys.argv[1]
    output_dir = sys.argv[2]

    split_multiband_tif(input_tif, output_dir)
