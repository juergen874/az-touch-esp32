import sys
import os
import time
import socket
import struct
import webrepl_cli

def esp_exec(code, host="192.168.188.123", port=8266, passwd="Servus", timeout=8.0):
    s = socket.socket()
    ai = socket.getaddrinfo(host, port)
    s.connect(ai[0][4])
    webrepl_cli.client_handshake(s)
    ws = webrepl_cli.websocket(s)
    webrepl_cli.login(ws, passwd)
    
    # Drain login messages
    time.sleep(0.1)
    ws.buf = b""
    
    # Send Ctrl-C to interrupt any running script
    ws.write(b"\r\x03\x03", frame=0x81)
    time.sleep(0.2)
    
    # Enter raw REPL: Ctrl-A
    ws.write(b"\x01", frame=0x81)
    time.sleep(0.2)
    
    # Read until raw REPL prompt '>'
    s.settimeout(2.0)
    raw_ready = False
    start_t = time.time()
    while time.time() - start_t < 2.0:
        try:
            c = ws.read(1, text_ok=True)
            if not c:
                break
            if c == b">":
                raw_ready = True
                break
        except Exception:
            break
            
    # Clear any residual buffer
    ws.buf = b""
    
    # Send code
    code_bytes = code.encode("utf-8")
    for i in range(0, len(code_bytes), 256):
        ws.write(code_bytes[i:i+256], frame=0x81)
        time.sleep(0.005)
    ws.write(b"\x04", frame=0x81)
    
    # Read response
    s.settimeout(timeout)
    output = b""
    start_t = time.time()
    while time.time() - start_t < timeout:
        try:
            c = ws.read(1, text_ok=True)
            if not c:
                break
            output += c
            if output.count(b"\x04") >= 2:
                break
        except socket.timeout:
            break
        except Exception:
            break
            
    try:
        ws.write(b"\x02", frame=0x81)
    except:
        pass
    s.close()
    
    if b"OK" in output:
        payload = output.split(b"OK", 1)[1]
        parts = payload.split(b"\x04")
        stdout = parts[0].decode("utf-8", errors="replace") if len(parts) > 0 else ""
        stderr = parts[1].decode("utf-8", errors="replace") if len(parts) > 1 else ""
        return stdout, stderr
    return output.decode("utf-8", errors="replace"), ""

if __name__ == "__main__":
    code = "import os; print('ESP files:', os.listdir())"
    if len(sys.argv) > 1:
        code = sys.argv[1]
    out, err = esp_exec(code)
    print("STDOUT:", out)
    if err:
        print("STDERR:", err)
