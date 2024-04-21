from re import A
import sys
from webui import uvr, uvr5_names

# MODEL_NAME = "HP2_all_vocals"
MODEL_NAME = "HP5_only_main_vocal"
AUDIO_FORMAT = "wav"


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python cli.py <input_folder> <output_vocal_folder> <output_instrumental_folder>"
        )
        sys.exit(1)

    input_folder = sys.argv[1]
    output_vocal_folder = sys.argv[2]
    output_instrumental_folder = sys.argv[3]
    model_name = MODEL_NAME
    audio_format = AUDIO_FORMAT

    if model_name not in uvr5_names:
        print(
            f"Error: Model {model_name} not found. Available models are: {uvr5_names}"
        )
        sys.exit(1)

    agg_default = 10

    uvr_processor = uvr(
        model_name,
        input_folder,
        output_vocal_folder,
        [],
        output_instrumental_folder,
        agg_default,
        audio_format,
    )

    print(f">>> Running model {model_name} on {input_folder}")
    try:
        for info in uvr_processor:
            print(info)
    except Exception as e:
        print(f"Error processing files: {e}")


if __name__ == "__main__":
    main()
