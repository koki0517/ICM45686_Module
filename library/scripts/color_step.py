"""Restore source component materials and board layer colors to assembly STEP.
Requires CadQuery 2.6+. Called by generate_library.py.
"""
from pathlib import Path
import sys
import cadquery as cq
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDF import TDF_LabelSequence
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.Quantity import Quantity_Color

ROOT=Path(__file__).resolve().parents[2]
MODELS=ROOT/'library/ICM45686_Module.3dshapes'

def restore_component(node,path):
 node._subshape_names.clear();node._subshape_colors.clear();node._subshape_layers.clear()
 reader=STEPCAFControl_Reader();reader.SetColorMode(True)
 reader.ReadFile(str(path))
 doc=TDocStd_Document(TCollection_ExtendedString('MDTV-XCAF'));reader.Transfer(doc)
 shape_tool=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
 color_tool=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
 labels=TDF_LabelSequence();shape_tool.GetFreeShapes(labels)
 assert labels.Length()==1
 node.obj=cq.Shape.cast(shape_tool.GetShape_s(labels.Value(1)))
 sublabels=TDF_LabelSequence();shape_tool.GetSubShapes_s(labels.Value(1),sublabels)
 inherited=[]
 for i,label in enumerate([labels.Value(1)]+[sublabels.Value(j) for j in range(1,sublabels.Length()+1)]):
  color=Quantity_Color()
  for kind in [XCAFDoc_ColorType.XCAFDoc_ColorSurf,XCAFDoc_ColorType.XCAFDoc_ColorGen]:
   if color_tool.GetColor_s(label,kind,color):
    material=cq.Color(color.Red(),color.Green(),color.Blue(),1,False)
    if i==0: node.color=material
    else: inherited.append((cq.Shape.cast(shape_tool.GetShape_s(label)).Faces(),material))
    break
 for face in node.obj.Faces():
  material=None
  for faces,col in inherited:
   if any(face.isSame(candidate) for candidate in faces): material=col
  color=Quantity_Color()
  for kind in [XCAFDoc_ColorType.XCAFDoc_ColorSurf,XCAFDoc_ColorType.XCAFDoc_ColorGen]:
   if color_tool.GetColor(face.wrapped,kind,color):
    material=cq.Color(color.Red(),color.Green(),color.Blue(),1,False);break
  if material is not None: node.addSubshape(face,color=material)

path=Path(sys.argv[1]) if len(sys.argv)>1 else MODELS/'ICM45686_Module.step'
output=Path(sys.argv[2]) if len(sys.argv)>2 else path
assembly=cq.Assembly.load(str(path))
module=assembly.children[0]
assert len(module.children)==10 and len(assembly.children)==6
for i in [0,2,3]:
 restore_component(module.children[i],Path('/usr/share/kicad/3dmodels/Capacitor_SMD.3dshapes/C_0402_1005Metric.step'))
restore_component(module.children[1],ROOT/'ICM_45686/ICM-45686.step')
for i in [1,3]: restore_component(assembly.children[i],Path('/usr/share/kicad/3dmodels/Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x04_P2.54mm_Vertical.step'))
for i in [2,4]: restore_component(assembly.children[i],Path('/usr/share/kicad/3dmodels/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step'))
module.children[4].color=cq.Color(0.82,0.70,0.30)
for i in [5,6]: module.children[i].color=cq.Color(0.95,0.95,0.92)
for i in [7,8]: module.children[i].color=cq.Color(0.08,0.28,0.15)
module.children[9].color=cq.Color(0.12,0.12,0.08)
assembly.children[5].color=cq.Color(0.82,0.70,0.30)
assembly.save(str(output),exportType='STEP')
assert 'COLOUR_RGB' in output.read_text()
print('Restored original component face colors and board layer colors:',output)
