import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox  # Agregar al inicio del archivo
from PIL import Image, ImageTk
import numpy as np
import cv2
from threading import Thread
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import urllib.request
import webbrowser


class REBNCONV(nn.Module):
    def __init__(self,in_ch=3,out_ch=3,dirate=1):
        super(REBNCONV,self).__init__()
        self.conv_s1 = nn.Conv2d(in_ch,out_ch,3,padding=1*dirate,dilation=1*dirate)
        self.bn_s1 = nn.BatchNorm2d(out_ch)
        self.relu_s1 = nn.ReLU(inplace=True)

    def forward(self,x):
        hx = x
        xout = self.relu_s1(self.bn_s1(self.conv_s1(hx)))
        return xout
### RSU-7 ###
class RSU7(nn.Module):
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU7,self).__init__()
        self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)
        self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
        self.pool1 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool2 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool3 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool4 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv5 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool5 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv6 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.rebnconv7 = REBNCONV(mid_ch,mid_ch,dirate=2)
        self.rebnconv6d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv5d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv4d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)
        self.upscore2 = nn.Upsample(scale_factor=2, mode='bilinear')
    def forward(self,x):
        hx = x
        hxin = self.rebnconvin(hx)
        hx1 = self.rebnconv1(hxin)
        hx = self.pool1(hx1)
        hx2 = self.rebnconv2(hx)
        hx = self.pool2(hx2)
        hx3 = self.rebnconv3(hx)
        hx = self.pool3(hx3)
        hx4 = self.rebnconv4(hx)
        hx = self.pool4(hx4)
        hx5 = self.rebnconv5(hx)
        hx = self.pool5(hx5)
        hx6 = self.rebnconv6(hx)
        hx7 = self.rebnconv7(hx6)
        hx6d =  self.rebnconv6d(torch.cat((hx7,hx6),1))
        hx6up = self.upscore2(hx6d)
        hx5d =  self.rebnconv5d(torch.cat((hx6up,hx5),1))
        hx5dup = self.upscore2(hx5d)
        hx4d = self.rebnconv4d(torch.cat((hx5dup,hx4),1))
        hx4dup = self.upscore2(hx4d)
        hx3d = self.rebnconv3d(torch.cat((hx4dup,hx3),1))
        hx3dup = self.upscore2(hx3d)
        hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
        hx2dup = self.upscore2(hx2d)
        hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
        return hx1d + hxin
### RSU-6 ###
class RSU6(nn.Module):
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU6,self).__init__()
        self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)
        self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
        self.pool1 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool2 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool3 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool4 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv5 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.rebnconv6 = REBNCONV(mid_ch,mid_ch,dirate=2)
        self.rebnconv5d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv4d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)
        self.upscore2 = nn.Upsample(scale_factor=2, mode='bilinear')
    def forward(self,x):
        hx = x
        hxin = self.rebnconvin(hx)
        hx1 = self.rebnconv1(hxin)
        hx = self.pool1(hx1)
        hx2 = self.rebnconv2(hx)
        hx = self.pool2(hx2)
        hx3 = self.rebnconv3(hx)
        hx = self.pool3(hx3)
        hx4 = self.rebnconv4(hx)
        hx = self.pool4(hx4)
        hx5 = self.rebnconv5(hx)
        hx6 = self.rebnconv6(hx5)
        hx5d =  self.rebnconv5d(torch.cat((hx6,hx5),1))
        hx5dup = self.upscore2(hx5d)
        hx4d = self.rebnconv4d(torch.cat((hx5dup,hx4),1))
        hx4dup = self.upscore2(hx4d)
        hx3d = self.rebnconv3d(torch.cat((hx4dup,hx3),1))
        hx3dup = self.upscore2(hx3d)
        hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
        hx2dup = self.upscore2(hx2d)
        hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
        return hx1d + hxin
### RSU-5 ###
class RSU5(nn.Module):
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU5,self).__init__()
        self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)
        self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
        self.pool1 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool2 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool3 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.rebnconv5 = REBNCONV(mid_ch,mid_ch,dirate=2)
        self.rebnconv4d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)
        self.upscore2 = nn.Upsample(scale_factor=2, mode='bilinear')
    def forward(self,x):
        hx = x
        hxin = self.rebnconvin(hx)
        hx1 = self.rebnconv1(hxin)
        hx = self.pool1(hx1)
        hx2 = self.rebnconv2(hx)
        hx = self.pool2(hx2)
        hx3 = self.rebnconv3(hx)
        hx = self.pool3(hx3)
        hx4 = self.rebnconv4(hx)
        hx5 = self.rebnconv5(hx4)
        hx4d = self.rebnconv4d(torch.cat((hx5,hx4),1))
        hx4dup = self.upscore2(hx4d)
        hx3d = self.rebnconv3d(torch.cat((hx4dup,hx3),1))
        hx3dup = self.upscore2(hx3d)
        hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
        hx2dup = self.upscore2(hx2d)
        hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
        return hx1d + hxin
### RSU-4 ###
class RSU4(nn.Module):
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU4,self).__init__()
        self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)
        self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
        self.pool1 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.pool2 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)
        self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=2)
        self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)
        self.upscore2 = nn.Upsample(scale_factor=2, mode='bilinear')
    def forward(self,x):
        hx = x
        hxin = self.rebnconvin(hx)
        hx1 = self.rebnconv1(hxin)
        hx = self.pool1(hx1)
        hx2 = self.rebnconv2(hx)
        hx = self.pool2(hx2)
        hx3 = self.rebnconv3(hx)
        hx4 = self.rebnconv4(hx3)
        hx3d = self.rebnconv3d(torch.cat((hx4,hx3),1))
        hx3dup = self.upscore2(hx3d)
        hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
        hx2dup = self.upscore2(hx2d)
        hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
        return hx1d + hxin
### RSU-4F ###
class RSU4F(nn.Module):
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU4F,self).__init__()
        self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)
        self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
        self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=2)
        self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=4)
        self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=8)
        self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=4)
        self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=2)
        self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)
    def forward(self,x):
        hx = x
        hxin = self.rebnconvin(hx)
        hx1 = self.rebnconv1(hxin)
        hx2 = self.rebnconv2(hx1)
        hx3 = self.rebnconv3(hx2)
        hx4 = self.rebnconv4(hx3)
        hx3d = self.rebnconv3d(torch.cat((hx4,hx3),1))
        hx2d = self.rebnconv2d(torch.cat((hx3d,hx2),1))
        hx1d = self.rebnconv1d(torch.cat((hx2d,hx1),1))
        return hx1d + hxin
##### U^2-Net ####
class U2NET(nn.Module):
    def __init__(self,in_ch=3,out_ch=1):
        super(U2NET,self).__init__()
        self.stage1 = RSU7(in_ch,32,64)
        self.pool12 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.stage2 = RSU6(64,32,128)
        self.pool23 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.stage3 = RSU5(128,64,256)
        self.pool34 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.stage4 = RSU4(256,128,512)
        self.pool45 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.stage5 = RSU4F(512,256,512)
        self.pool56 = nn.MaxPool2d(2,stride=2,ceil_mode=True)
        self.stage6 = RSU4F(512,256,512)
        # decoder
        self.stage5d = RSU4F(1024,256,512)
        self.stage4d = RSU4(1024,128,256)
        self.stage3d = RSU5(512,64,128)
        self.stage2d = RSU6(256,32,64)
        self.stage1d = RSU7(128,16,64)
        self.side1 = nn.Conv2d(64,1,3,padding=1)
        self.side2 = nn.Conv2d(64,1,3,padding=1)
        self.side3 = nn.Conv2d(128,1,3,padding=1)
        self.side4 = nn.Conv2d(256,1,3,padding=1)
        self.side5 = nn.Conv2d(512,1,3,padding=1)
        self.side6 = nn.Conv2d(512,1,3,padding=1)
        self.upscore6 = nn.Upsample(scale_factor=32,mode='bilinear')
        self.upscore5 = nn.Upsample(scale_factor=16,mode='bilinear')
        self.upscore4 = nn.Upsample(scale_factor=8,mode='bilinear')
        self.upscore3 = nn.Upsample(scale_factor=4,mode='bilinear')
        self.upscore2 = nn.Upsample(scale_factor=2, mode='bilinear')
        self.outconv = nn.Conv2d(6,1,1)
    def forward(self,x):
        hx = x
        #stage 1
        hx1 = self.stage1(hx)
        hx = self.pool12(hx1)
        #stage 2
        hx2 = self.stage2(hx)
        hx = self.pool23(hx2)
        #stage 3
        hx3 = self.stage3(hx)
        hx = self.pool34(hx3)
        #stage 4
        hx4 = self.stage4(hx)
        hx = self.pool45(hx4)
        #stage 5
        hx5 = self.stage5(hx)
        hx = self.pool56(hx5)
        #stage 6
        hx6 = self.stage6(hx)
        hx6up = self.upscore2(hx6)
        #-------------------- decoder --------------------
        hx5d = self.stage5d(torch.cat((hx6up,hx5),1))
        hx5dup = self.upscore2(hx5d)
        hx4d = self.stage4d(torch.cat((hx5dup,hx4),1))
        hx4dup = self.upscore2(hx4d)
        hx3d = self.stage3d(torch.cat((hx4dup,hx3),1))
        hx3dup = self.upscore2(hx3d)
        hx2d = self.stage2d(torch.cat((hx3dup,hx2),1))
        hx2dup = self.upscore2(hx2d)
        hx1d = self.stage1d(torch.cat((hx2dup,hx1),1))
        #side output
        d1 = self.side1(hx1d)
        d2 = self.side2(hx2d)
        d2 = self.upscore2(d2)
        d3 = self.side3(hx3d)
        d3 = self.upscore3(d3)
        d4 = self.side4(hx4d)
        d4 = self.upscore4(d4)
        d5 = self.side5(hx5d)
        d5 = self.upscore5(d5)
        d6 = self.side6(hx6)
        d6 = self.upscore6(d6)
        d0 = self.outconv(torch.cat((d1,d2,d3,d4,d5,d6),1))
        return F.sigmoid(d0), F.sigmoid(d1), F.sigmoid(d2), F.sigmoid(d3), F.sigmoid(d4), F.sigmoid(d5), F.sigmoid(d6)

class SimpleBackgroundRemover:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Background Remover")
        self.root.geometry("800x400")
        
        # Initialize variables
        self.status_var = tk.StringVar(value="Iniciando...")
        self.model = None
        self.original_image_path = None
        
        # Check model and create appropriate interface
        self.check_model()
    
    def check_model(self):
        """Check if model exists and create appropriate interface"""
        if not os.path.exists('models'):
            os.makedirs('models')
        
        model_path = 'models/u2net.pth'
        
        if not os.path.exists(model_path):
            self.create_download_interface()
        else:
            self.initialize_model()
            self.create_main_interface()
    
    def create_download_interface(self):
        """Create interface for model download"""
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        message_label = ttk.Label(frame, text="Se requiere descargar el modelo U2NET para continuar.", 
                                wraplength=500)
        message_label.grid(row=0, column=0, pady=20)
        
        download_button = ttk.Button(frame, text="Descargar Modelo",
                                   command=self.open_download_link)
        download_button.grid(row=1, column=0, pady=10)
        
        restart_button = ttk.Button(frame, text="Reiniciar Aplicación",
                                  command=self.restart_app)
        restart_button.grid(row=2, column=0, pady=10)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_main_interface(self):
        """Create main interface for image processing"""
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Image selection button
        select_button = ttk.Button(frame, text="Seleccionar Imagen",
                                 command=self.load_image)
        select_button.grid(row=0, column=0, pady=10)
        
        # Process button
        self.process_button = ttk.Button(frame, text="Remover Fondo",
                                       command=self.process_image,
                                       state='disabled')
        self.process_button.grid(row=1, column=0, pady=10)
        
        # Status label
        status_label = ttk.Label(frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, length=300, mode='determinate')
        self.progress.grid(row=3, column=0, pady=10)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def open_download_link(self):
        webbrowser.open("https://drive.google.com/file/d/1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ/view")
    
    def restart_app(self):
        self.root.destroy()
        self.__init__()
        self.run()
    
    def initialize_model(self):
        try:
            from u2net import U2NET  # Assuming u2net.py is in the same directory
            self.model = U2NET()
            self.model.load_state_dict(torch.load('models/u2net.pth', 
                                     map_location=torch.device('cpu' if not torch.cuda.is_available() else 'cuda')))
            self.model.eval()
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            self.status_var.set("Modelo cargado correctamente")
        except Exception as e:
            self.status_var.set(f"Error al cargar el modelo: {str(e)}")
    
    def load_image(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            self.original_image_path = file_path
            self.status_var.set("Imagen cargada: " + os.path.basename(file_path))
            self.process_button.configure(state='normal')
    
    def normalize_image(self, img):
        img = img.astype(np.float32) / 255.0
        img = img.transpose((2, 0, 1))
        img = torch.from_numpy(img).unsqueeze(0)
        if torch.cuda.is_available():
            img = img.cuda()
        return img
    
    def process_image(self):
        if not self.original_image_path:
            return
        
        self.status_var.set("Procesando imagen...")
        self.progress['value'] = 0
        Thread(target=self._process_thread).start()
    
    def _process_thread(self):
        try:
            # Load and preprocess image
            image = Image.open(self.original_image_path)
            img_np = np.array(image)
            self.progress['value'] = 30
            
            # Process with model
            img = cv2.resize(img_np, (320, 320))
            img = self.normalize_image(img)
            
            with torch.no_grad():
                mask, *_ = self.model(img)
                mask = F.interpolate(mask, size=img_np.shape[:2], 
                                   mode='bilinear', align_corners=True)
                mask = mask.squeeze().cpu().numpy()
            
            self.progress['value'] = 60
            
            # Apply mask
            mask = (mask * 255).astype(np.uint8)
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2RGBA)
            img_np[:, :, 3] = mask
            
            # Save result
            output_path = os.path.splitext(self.original_image_path)[0] + "_no_bg.png"
            result_image = Image.fromarray(img_np)
            result_image.save(output_path, "PNG", quality=100)
            
            self.progress['value'] = 100
            self.status_var.set(f"Imagen guardada como: {os.path.basename(output_path)}")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleBackgroundRemover()
    app.run()