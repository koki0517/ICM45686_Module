#!/usr/bin/python3
"""Rebuild KiCad 9 carrier libraries and STEP assemblies from the source board."""
from pathlib import Path
import argparse, subprocess, tempfile, sys
import pcbnew
ROOT=Path(__file__).resolve().parents[2]
LIB=ROOT/'library'
NAME='ICM45686_Module'
MODELS=LIB/(NAME+'.3dshapes')
FPDIR=LIB/(NAME+'.pretty')
ORIGIN=(68.58,43.942)
HEIGHT=11.04  # 8.50 mm socket + 2.54 mm header insulator

def run(*args):
 subprocess.run(['kicad-cli',*map(str,args)],check=True)

def model(path,x=0,y=0,z=0,rx=0,rz=0):
 return f'(model "{path}" (offset (xyz {x} {y} {z})) (scale (xyz 1 1 1)) (rotate (xyz {rx} 0 {rz})))'

def footprint(model_path=None, model_statements=None):
 name=NAME
 s=f'''(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu")
 (descr "ICM-45686 module; carrier-side pin sockets with downward module pin headers; 2x 1x04 P2.54mm, row spacing 10.16mm")
 (tags "ICM45686 IMU module pin socket header assembly") (attr through_hole)
 (fp_text reference "REF**" (at 5.08 -3.4) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (fp_text value "{name}" (at 5.08 11.2) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
'''
 # Exact source outline on fabrication and drawing layers, never on carrier Edge.Cuts.
 b=pcbnew.LoadBoard(str(ROOT/'ICM-45686.kicad_pcb'))
 def xy(p): return f'{pcbnew.ToMM(p.x)-ORIGIN[0]:.6f} {pcbnew.ToMM(p.y)-ORIGIN[1]:.6f}'
 for layer in ['F.Fab','Dwgs.User']:
  for g in b.GetDrawings():
   if g.GetLayer()!=pcbnew.Edge_Cuts: continue
   if g.GetShape()==pcbnew.SHAPE_T_ARC:
    s+=f'(fp_arc (start {xy(g.GetStart())}) (mid {xy(g.GetArcMid())}) (end {xy(g.GetEnd())}) (stroke (width 0.1) (type solid)) (layer "{layer}"))\n'
   else: s+=f'(fp_line (start {xy(g.GetStart())}) (end {xy(g.GetEnd())}) (stroke (width 0.1) (type solid)) (layer "{layer}"))\n'
 s+='(fp_rect (start -2.3 -3.05) (end 12.45 10.7) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))\n'
 s+='(fp_rect (start -1.95 -2.7) (end 12.1 10.35) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))\n'
 for row,x in enumerate([0,10.16]):
  s+=f'(fp_rect (start {x-1.27} -1.27) (end {x+1.27} 8.89) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))\n'
  for i in range(4):
   n=row*4+i+1
   s+=f'(pad "{n}" thru_hole {"rect" if i==0 else "oval"} (at {x} {i*2.54}) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))\n'
 s+='(fp_circle (center -1.25 -1.25) (end -1.05 -1.25) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))\n'
 s+=(model_statements if model_statements is not None else model(model_path,z=-1.595))+'\n)\n'
 return s

def symbol():
 name=NAME
 s=f'''(symbol "{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
 (property "Reference" "U" (at 0 13.97 0) (effects (font (size 1.27 1.27))))
 (property "Value" "{name}" (at 0 11.43 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "{NAME}:{name}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Description" "ICM-45686 SPI module, carrier-side pin sockets with downward module pin headers, 3.3V supply" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "ki_fp_filters" "{NAME}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (symbol "{name}_0_1" (rectangle (start -7.62 10.16) (end 7.62 -10.16) (stroke (width 0.254) (type default)) (fill (type background))))
 (symbol "{name}_1_1"
'''
 pins=[(1,'3V3','power_in',0,12.7,270),(2,'GND','power_in',0,-12.7,90),(3,'SCLK','input',-10.16,5.08,0),(4,'MISO','output',10.16,5.08,180),(5,'INT','output',10.16,0,180),(6,'FSYNC','input',-10.16,-5.08,0),(7,'MOSI','input',-10.16,0,0),(8,'CS','input',-10.16,7.62,0)]
 for n,label,kind,x,y,a in pins:
  s+=f'(pin {kind} line (at {x} {y} {a}) (length 2.54) (name "{label}" (effects (font (size 1.27 1.27)))) (number "{n}" (effects (font (size 1.27 1.27)))))\n'
 return s+'))\n'

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--cadquery-python',default=sys.executable,help='Python interpreter with CadQuery 2.6+')
 args=parser.parse_args()
 subprocess.run([args.cadquery_python,'-c','import cadquery'],check=True)
 MODELS.mkdir(parents=True,exist_ok=True); FPDIR.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='icm-library-') as tmp:
  tmp=Path(tmp)
  b=pcbnew.LoadBoard(str(ROOT/'ICM-45686.kicad_pcb'))
  for f in b.GetFootprints():
   f.Models().clear()
   if f.GetReference()=='U1': path=ROOT/'ICM_45686/ICM-45686.step'
   elif f.GetReference().startswith('C'): path=Path('/usr/share/kicad/3dmodels/Capacitor_SMD.3dshapes/C_0402_1005Metric.step')
   else: continue
   m=pcbnew.FP_3DMODEL(); m.m_Filename=str(path)
   # Source STEP is Y-up: rotate onto the PCB so thickness is along Z.
   if f.GetReference()=='U1': m.m_Rotation.x=-90
   f.Models().push_back(m)
  pcbnew.SaveBoard(str(tmp/'module.kicad_pcb'),b)
  run('pcb','export','step','--force','--user-origin','68.58x43.942mm','--include-pads','--include-soldermask','--include-silkscreen','-o',tmp/'ICM45686_Module_Bare.step',tmp/'module.kicad_pcb')
  # Assembly export uses a 1.6mm carrier. Footprint model offset removes it.
  s=footprint('unused')
  s=s[:s.rfind('(model')]
  s+=model(tmp/'ICM45686_Module_Bare.step',z=HEIGHT)+'\n'
  for x in [0,10.16]:
   host=Path(f'/usr/share/kicad/3dmodels/Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x04_P2.54mm_Vertical.step')
   mate=Path(f'/usr/share/kicad/3dmodels/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step')
   s+=model(host,x=x)+'\n'+model(mate,x=x,z=HEIGHT,rx=180,rz=180)+'\n'
  s+=')'
  (tmp/f'{NAME}.kicad_mod').write_text(s)
  f=pcbnew.FootprintLoad(str(tmp),f'{NAME}'); f.SetReference('U1')
  hostboard=pcbnew.BOARD(); hostboard.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.6)); hostboard.Add(f)
  for a,c in [((-5,-5),(16,-5)),((16,-5),(16,14)),((16,14),(-5,14)),((-5,14),(-5,-5))]:
   g=pcbnew.PCB_SHAPE(); g.SetShape(pcbnew.SHAPE_T_SEGMENT); g.SetLayer(pcbnew.Edge_Cuts); g.SetStart(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in a])); g.SetEnd(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in c])); hostboard.Add(g)
  pcbnew.SaveBoard(str(tmp/'assembly.kicad_pcb'),hostboard)
  run('pcb','export','step','--force','--no-board-body','--include-pads','--user-origin','0x0mm','-o',tmp/f'{NAME}.step',tmp/'assembly.kicad_pcb')
  subprocess.run([args.cadquery_python,str(Path(__file__).with_name('color_step.py')),str(tmp/f'{NAME}.step'),str(MODELS/f'{NAME}.step')],check=True)
  target=f'${{ICM45686_MODULE_DIR}}/{NAME}.3dshapes/{NAME}.step'
  (FPDIR/f'{NAME}.kicad_mod').write_text(footprint(target))
  review=footprint(str(MODELS/f'{NAME}.step'))
  (tmp/f'{NAME}.kicad_mod').write_text(review)
  hostboard.Remove(f); hostboard.Add(pcbnew.FootprintLoad(str(tmp),f'{NAME}'))
  pcbnew.SaveBoard(str(tmp/f'review_PinSocket.kicad_pcb'),hostboard)
  run('pcb','render','--width','1100','--height','850','--background','opaque','--zoom','0.65','--pan','0,0,0.6','--rotate','-65,0,25','-o',LIB/'preview'/'Assembly.png',tmp/f'review_PinSocket.kicad_pcb')
 (LIB/f'{NAME}.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+symbol()+')\n')
if __name__=='__main__': main()
