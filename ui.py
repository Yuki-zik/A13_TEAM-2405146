# Team Linear Regression
# Date: 2024-04-13

print("\n=== Vocal Conversion by Team Linear Regression ===")
print("\nLoading UI...")

import io, os, sys, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(__file__))

if not os.path.exists("tools"):
    print("\n警告：找不到组件文件夹，请检查安装是否完整！")
    os.system("pause")
    os._exit(1)
os.environ["PATH"] += os.pathsep + os.path.abspath("tools/ffmpeg")
io.text_encoding = lambda x: "utf-8"  # fix gradio cannot read this code file

from matplotlib.pylab import f
import gradio as gr
import infer_bridge as model


def gettime():
    return time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())


def updatelog(log, msg):
    log[0] += f"{gettime()} {msg}\n"
    return log[0]


with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue"), title="歌声转换") as app:
    gr.Markdown(
        """
        # 歌声转换 by Team Linear Regression
        输入一段歌唱音频，将其转换为指定歌手的风格。


        **使用方法**：
        1. 上传要转换的音频，设置目标歌手及相关参数。如音频包含伴奏，需开启人声分离功能。
        2. 点击“开始”按钮，等待生成结果。
        3. 点击输入音频右方小箭头，可下载结果音频。
        """
    )
    with gr.Row():
        with gr.Column():
            gr.Markdown("## 操作面板")
            singer = gr.Radio(
                choices=list(model.SINGERS.keys()),
                label="目标歌手",
                value=list(model.SINGERS.keys())[0],
            )
            vocal_sep = gr.Radio(
                choices=["开启", "关闭"],
                value="开启",
                label="人声分离",
                info="开启后，输入音频将被分离为人声和伴奏两部分，仅人声部分会被转换，输出时合并到一起",
            )
            keyshift_mode = gr.Radio(
                choices=["自动", "手动"],
                value="自动",
                label="音高控制",
                info="自动模式下，系统将自动检测音高并调整到最佳效果",
            )
            keyshift_value = gr.Slider(
                -6,
                6,
                value=0,
                step=1,
                label="手动音高偏移值",
                info="手动设置音高升降多少个半音",
                visible=False,
            )
            keyshift_mode.change(
                (lambda choice: gr.update(visible=choice == "手动")),
                [keyshift_mode],
                [keyshift_value],
            )
            steps = gr.Slider(
                model.STEP_RANGE[0],
                model.STEP_RANGE[1],
                value=model.STEP_RANGE[2],
                step=1,
                label="推理步数",
                info="步数越多，结果越好，耗时越长",
            )
            reset_btn = gr.Button(value="重置", variant="secondary")
            start_btn = gr.Button(value="开始", variant="primary")

        with gr.Column():
            gr.Markdown("## 音频文件")
            input_file = gr.Audio(label="输入音频", type="filepath", sources=["upload"])
            output_file = gr.Audio(label="输出音频", type="filepath")
            with gr.Column():
                running_status = gr.Textbox(
                    label="运行信息",
                    placeholder="等待中...",
                    interactive=False,
                    info="此处仅显示完成状态，模型推理进度可前往命令行窗口查看",
                )
                progress = gr.Slider(0, 100, 0, step=1, label="进度条", visible=False)

    @reset_btn.click(
        outputs=[
            singer,
            vocal_sep,
            keyshift_mode,
            keyshift_value,
            steps,
            input_file,
            output_file,
            running_status,
            progress,
        ]
    )  # type: ignore
    def reset():
        return (
            list(model.SINGERS.keys())[0],
            "开启",
            "自动",
            0,
            model.STEP_RANGE[2],
            None,
            None,
            "等待中...",
            gr.Slider(0, 100, 0, step=1, label="进度条", visible=False),
        )

    @start_btn.click(
        inputs=[input_file, singer, vocal_sep, keyshift_mode, keyshift_value, steps],
        outputs=[output_file, running_status, progress],
    )  # type: ignore
    def run_model(
        filepath,
        singer,
        vocal_sep="开启",
        keyshift_mode="自动",
        keyshift=0,
        steps=model.STEP_RANGE[1],
    ):
        print("\n### Start converting...")
        log = [f'输入文件："{filepath}"\n']
        yield (
            None,
            log[0],
            gr.Slider(0, 100, 0, step=1, label="进度条", visible=True),
        )
        yield (None, updatelog(log, "开始转换"), 0)

        try:
            if not filepath:
                print("No file uploaded")
                print("\n### Error")
                yield (None, updatelog(log, "错误：未上传文件"), 100)
                return

            filepath = filepath.replace("\\", "/")  # xxx/xxx/abc.mp3
            audio_dir = "/".join(filepath.split("/")[:-1])  # xxx/xxx
            audio_file = filepath.split("/")[-1]  # abc.mp3
            audio_name = "".join(audio_file.split(".")[:-1])  # abc
            audio_ext = audio_file.split(".")[-1]  # mp3

            singer = model.SINGERS[singer]

            if vocal_sep == "开启":
                vocal_sep = True
            else:
                vocal_sep = False

            if keyshift_mode == "自动":
                keyshift = "autoshift"
                keyshift_str = ""
            else:
                keyshift = keyshift
                keyshift_str = " +" if keyshift >= 0 else " "
                keyshift_str += f"{keyshift}"

            print(f'"{audio_file}" -> {singer}{keyshift_str}, {steps}steps')
            if not os.path.exists(filepath):
                print(f"File not exist: {filepath}")
                print("\n### Error")
                yield (None, updatelog(log, "错误：上传的文件不存在"), 100)
                return

            model.init()

            vocal_path = filepath
            if vocal_sep:
                yield (
                    None,
                    updatelog(log, "正在进行人声分离，预计需要 5 分钟左右..."),
                    0,
                )
                vocal_path, inst_path = model.vocal_sep(
                    filepath, audio_file, audio_name, audio_ext
                )
                yield (None, updatelog(log, "人声分离已完成"), 30)

            yield (None, updatelog(log, "正在进行人声转换，请稍候..."), 30)
            vocal_conv_path = model.run(vocal_path, audio_name, singer, keyshift, steps)

            if not os.path.exists(vocal_conv_path):
                print(f"Vocal conversion failed. No result was generated.")
                print("\n### Error")
                yield (None, updatelog(log, "错误：转换失败，未生成结果音频"), 100)
                return
            yield (None, updatelog(log, "人声转换已完成"), 90)

            final_path = vocal_conv_path
            if vocal_sep:
                yield (None, updatelog(log, "正在合并人声和伴奏..."), 90)
                final_path = model.vocal_merge(vocal_conv_path, inst_path, audio_name)  # type: ignore

            yield (None, updatelog(log, "正在整理最终结果..."), 95)
            result = model.finalize(final_path, audio_name, singer)

            print("\n### Done")
            yield (
                result,
                updatelog(
                    log,
                    f'转换成功！\n输出文件："{result}"\n也可点击输出音频右侧下载按钮下载结果',
                ),
                100,
            )
            return
        except:
            import traceback

            trace = traceback.format_exc()
            print(f"\n### Script error:\n\n{trace}")
            yield (None, updatelog(log, f"运行错误：\n\n{trace}"))


if __name__ == "__main__":
    print(
        "\n如果页面没有自动打开或者连接错误，请检查是否开启了网络代理、6789端口是否被占用，处理后关闭并重新打开本程序\n"
    )
    app.launch(
        inbrowser=True,
        server_name="localhost",
        server_port=6789,
        favicon_path="./tools/logo.ico",
    )
