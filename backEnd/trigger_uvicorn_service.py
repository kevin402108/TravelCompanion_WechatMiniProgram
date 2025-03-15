import http.server
import socketserver
import subprocess
import os
import sys
import platform




# 获取环境变量，默认生产环境
app_env = os.getenv('ENVIRONMENT', 'production') 

def get_script_path():
    sys = platform.system()
    script_name = f"start_uvicorn_{'dev' if app_env == 'development' else 'prod'}"
    if sys == "Windows":
        return os.path.join(os.getcwd(),"travel_companion_system",f"{script_name}.ps1")
    elif sys == "Linux":
        return os.path.join(os.getcwd(),"travel_companion_system",f"{script_name}.sh")
    return None

class UvicornStarter(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        breakpoint()
        if self.path == "/start_uvicorn":
            script_path = get_script_path()
            if script_path:
                try:
                    if platform.system() == "Windows":
                        subprocess.run(["powershell.exe","-File",script_path],check=True)
                    else:
                        subprocess.run([script_path],check=True)
                    self.send_response(200)
                    self.send_header('Content-type','text-plain')
                    self.end_headers()
                    self.wfile.write("uvicorn startup success".encode())
                except subprocess.CalledProcessError as err:
                    self.send_response(500)
                    self.send_header('Content-type','text-plain')
                    self.end_headers()
                    self.wfile.write(f"uvicorn启动失败：{err}".encode())
            else:
                self.send_response(404)
                self.send_header('Content-type','text/plain')
                self.end_headers()
                self.wfile.write("Failed to find the script!".encode())
                
if __name__ == "__main__":
    PORT = 8002
    with socketserver.TCPServer(("",PORT),UvicornStarter) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()  