from tempfile import tempdir
import os, shutil, time

SINGERS: dict = {
    "阿黛尔 (Adele)": "adele",
    "贾斯汀 (Justin)": "justin",
    "泰勒 (Taylor)": "taylor",
    "特朗普 (Trump)": "trump",
    "塞壬": "alto-6",
}

STEP_RANGE: tuple = (1, 100, 40)


def init():
    # clean temp
    shutil.rmtree("temp", ignore_errors=True)
    os.makedirs("temp", exist_ok=True)


def run(vocalpath, filename, singer, keyshift, steps):
    input_path = os.path.abspath(vocalpath)
    output_path = os.path.abspath(f"temp/{filename}_output.wav")
    print("\n--- SVC vocal conversion ---")

    amphion = os.path.abspath("tools/Amphion/Amphion.bat")

    # Usage ./tools/Amphion/Amphion.bat <input_file> <output_file> <singer> <keyshift> <steps>
    cmd = f'cmd /c call "{amphion}" "{input_path}" "{output_path}" {singer} {keyshift} {steps}'
    print(">>>", cmd)
    cmd_err = os.system(cmd)
    if cmd_err != 0 or not os.path.exists(output_path):
        raise Exception("Error running SVC")

    print("--- SVC over ---")
    return output_path


def vocal_sep(path, file, name, ext):
    vocal_path = f"temp/{name}_vocal.wav"
    inst_path = f"temp/{name}_inst.wav"
    print("\n--- UVR5 vocal separation ---")

    os.makedirs("temp/vocal", exist_ok=True)
    os.makedirs("temp/inst", exist_ok=True)
    shutil.copyfile(path, os.path.join("temp", file))
    if ext.lower() == "wav":
        tmpdir = os.environ["TEMP"]
        shutil.copyfile(path, os.path.join(tmpdir, f"{file}.reformatted.wav"))
    uvr5 = os.path.abspath("tools/uvr5/UVR5.bat")
    tempdir = os.path.abspath("temp")
    vocaldir = os.path.abspath("temp/vocal")
    instdir = os.path.abspath("temp/inst")

    # Usage ./tools/uvr5/UVR5.bat <input_folder> <output_vocal_folder> <output_instrumental_folder>
    cmd = f'cmd /c call "{uvr5}" "{tempdir}" "{vocaldir}" "{instdir}"'
    print(">>>", cmd)
    cmd_err = os.system(cmd)
    if cmd_err != 0:
        raise Exception("Error running UVR5")

    # Rename the output files
    # temp/vocal/* -> temp/<filename>_vocal.wav
    # temp/inst/* -> temp/<filename>_inst.wav
    # Delete temp/vocal and temp/inst
    try:
        vocal_file = os.listdir("temp/vocal")[0]
        os.rename(f"temp/vocal/{vocal_file}", vocal_path)
        inst_file = os.listdir("temp/inst")[0]
        os.rename(f"temp/inst/{inst_file}", inst_path)
        shutil.rmtree("temp/vocal")
        shutil.rmtree("temp/inst")
    except:
        raise Exception("Error running UVR5")

    print("--- UVR5 over ---")
    return vocal_path, inst_path


def vocal_merge(vocal_file, inst_file, filename):
    # Use ffmpeg to merge the vocal and instrumental files
    # Output -> temp/<filename>_final.wav
    print("\n--- FFmpeg final mix ---")
    final_path = f"temp/{filename}_final.wav"
    cmd = f'ffmpeg -i "{vocal_file}" -i "{inst_file}" -filter_complex amix=inputs=2:duration=first:dropout_transition=2 "{final_path}"'
    print(">>>", cmd)
    cmd_err = os.system(cmd)
    if cmd_err != 0:
        raise Exception("Error running FFmpeg")
    print("--- FFmpeg over ---")
    return final_path


def finalize(final_path, name, singer):
    current_time = time.strftime("%Y%m%d_%H%M%S")
    result_path = f"result/{name}_{singer}_{current_time}.wav"
    print(f'\nCopying "{final_path}" -> "{result_path}"')
    shutil.copyfile(final_path, result_path)
    return result_path
