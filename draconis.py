import argparse
import json
import os.path
import tempfile

import requests

from draconis_parser.helper_functions import parse_pou_file
from draconis_parser.renderer import render_program_to_svg, self_contained_style_header

def upload_single_model(server, model_path, metrics_path, project_name):
    # Prepare the files parameter with open files
    try:
        with open(model_path, 'rb') as program_file, open(metrics_path, 'rb') as metrics_file:
            files = {
                "program_file_path": program_file,
                "metrics_file_path": metrics_file
            }
            # Send the POST request with files
            response = requests.post(f"http://{server}/batch", files=files, data={"project_name":project_name})

            # Check the response status
            if response.status_code == 200:
                print(f"Successfully uploaded: {model_path} and {metrics_path}")
            else:
                print(f"Failed to upload: {response.status_code} - {response.text}")
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

def batch_upload(target_data, server):
    print(f"Uploading to server: {server}")
    for entry in target_data:
        program_file_path = entry.get("model", None)
        metrics_file_path = entry.get("additional_metrics", None)
        if program_file_path and metrics_file_path:
            upload_single_model(server, program_file_path, metrics_file_path)
        else:
            print("Missing model or metrics information in entry.")
            print(program_file_path)
            print(metrics_file_path)


def render_model(model_file, result_svg_path):
    if not (os.path.isfile(model_file)):
        return None

    aProgram = parse_pou_file(model_file)
    w, h, svg_content = render_program_to_svg(aProgram, scale=7.0)
    style_css = self_contained_style_header()
    result_fp = result_svg_path + ".html"
    with open(result_fp, "w") as svg_file:
        svg_file.write(f'<html><head>{style_css}</head><body>\n<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">{svg_content}</svg></body></html>')
    return result_fp


def add_metrics(target_model_id, target_metrics_json_file, server):
    if os.path.isfile(target_metrics_json_file):
        try:
            with open(target_metrics_json_file, 'rb') as metrics_file:
                files = {
                    "additional_metrics": metrics_file
                }
                # Send the POST request with files
                response = requests.post(f"http://{server}/{target_model_id}/append_metrics", files=files)

                # Check the response status
                if response.status_code == 200:
                    print(f"Successfully connected metrics to model {target_model_id}")
                else:
                    print(f"Failed to upload: {response.status_code} - {response.text}")
        except FileNotFoundError as e:
            print(f"File error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

def main():
    parser = argparse.ArgumentParser(description="DRACONIS Command Line Tool")
    parser.add_argument("--server", default="localhost:8000", help="Server IP (defaults to localhost:8000)")
    parser.add_argument("--project-name", required=False,
                                    default="UNKNOWN",
                                    help="Name of project to associate models with")
    subparsers = parser.add_subparsers(dest="command")

    upload_parser = subparsers.add_parser("upload", help="Upload analyses to server")
    upload_parser.add_argument("--target", required=True, help="Path to JSON file containing analyses")

    upload_dir_parser = subparsers.add_parser("upload-dir", help="Upload data from a directory to server")
    upload_dir_parser.add_argument("--target-dir", required=True, help="Path to directory containing data")

    add_metrics_parser = subparsers.add_parser("add-metric", help="Add additional metrics to existing model")
    add_metrics_parser.add_argument("--model", required=True, help="Model ID in DRACONIS")
    add_metrics_parser.add_argument("--metrics-file", required=True, help="file to upload - JSON")

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument('--model-path', required=True, help="Path to model file")
    render_parser.add_argument('--output-path', required=True,
                               help="Path to SVG output file. Will be overwritten if it exists")

    render_parser = subparsers.add_parser("render-all")
    render_parser.add_argument('--models-directory', required=True, help="Path to model file")

    args = parser.parse_args()

    if args.command == "upload":
        # Load and parse the JSON file specified in --target
        with open(args.target, 'r') as f:
            target_data = json.load(f)

        # Pass parsed data to upload function
        batch_upload(target_data, args.server)

    if args.command == "upload-dir":
        # make a temporary metrics file to deal with files that do not come with metrics
        with tempfile.NamedTemporaryFile(delete=False) as empty_metrics:
            empty_metrics.write(b'{}')
            empty_metrics.close()

            assert os.path.isdir(args.target_dir)

            for top, _, all_files in os.walk(args.target_dir):
                pou_files = [(os.path.join(top, f), os.path.splitext(f)[0]) for f in all_files if os.path.splitext(f)[1] == ".pou"]
                # Assume metrics are stored in json files
                metrics_files = [(os.path.join(top, f), os.path.splitext(f)[0]) for f in all_files if os.path.splitext(f)[1] == ".json"]

                for (pou, name) in pou_files:
                    # if a metrics file exists, use that. Else use the dummy file
                    metrics_files_found = [m for (m, mname) in metrics_files if name == mname]
                    assert (len(metrics_files_found) <= 1) # Only works if we do not have multiple files with the same name
                    metrics_file = metrics_files_found[0] if metrics_files_found != [] else empty_metrics.name

                    upload_single_model(args.server, pou, metrics_file, args.project_name)





    if args.command == "add-metric":
        add_metrics(args.model, args.metrics_file, args.server)

    if args.command == "render":
        res_path = render_model(args.model_path, args.output_path)
        if res_path is not None:
            print("Render created at " + res_path)
        else:
            print("Something has gone wrong during the rendering")

    if args.command == "render-all":
        all_files = os.listdir(args.models_directory)
        pou_files = [f for f in all_files if os.path.splitext(f)[1] == ".pou"]
        for pou in pou_files:
            res_path = render_model(os.path.join(args.models_directory, pou), os.path.join(args.models_directory, pou + ".svg"))
            if res_path is None:
                print(f"Failed during render of {pou}")
                continue




if __name__ == "__main__":
    main()
