import pathlib,json,base64,hashlib,time,gmsh
root=pathlib.Path(__file__).parent
driver=root.parent/'qa_driver.py'
ns={'__file__':str(driver)};exec(driver.read_text().split("head=Client")[0],ns)
head=ns['Client'](['--headless'],'structural-step')
try:
    model=ns['source']/'current.model.json'
    head.tool('cad_load_project_model',{'model_json':model.read_text(encoding='utf-8')})
    before=head.tool('cad_project_model',{})
    result=head.tool('solid_export_step',{'body_ids':[173]})
    data=base64.b64decode(result['bytes_base64']);(root/'clip-173.step').write_bytes(data)
    assert head.tool('cad_project_model',{})==before
finally:head.close()
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
gmsh.option.setString('Geometry.OCCTargetUnit','MM');gmsh.model.add('clip')
start=time.perf_counter();volumes=gmsh.model.occ.importShapes(str(root/'clip-173.step'));gmsh.model.occ.synchronize()
faces=gmsh.model.getEntities(2)
for dim,tag in volumes:gmsh.model.addPhysicalGroup(dim,[tag],name=f'body173_volume{tag}')
for dim,tag in faces:gmsh.model.addPhysicalGroup(dim,[tag],name=f'imported_face_{tag}')
gmsh.option.setNumber('Mesh.MeshSizeMin',.8);gmsh.option.setNumber('Mesh.MeshSizeMax',.8)
gmsh.option.setNumber('Mesh.MaxNumThreads3D',1)
gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
types,ids,connect=gmsh.model.mesh.getElements(3)
quality=list(gmsh.model.mesh.getElementQualities(ids[0],'minSICN'))
before_quality=dict(min_sicn=min(quality),nonpositive=sum(q<=0 for q in quality))
gmsh.model.mesh.optimize('HighOrder')
quality=list(gmsh.model.mesh.getElementQualities(ids[0],'minSICN'))
gmsh.write(str(root/'clip-173.msh'))
result=dict(body_id=173,step_sha256=hashlib.sha256(data).hexdigest(),volumes=len(volumes),faces=len(faces),
    volume_mm3=sum(gmsh.model.occ.getMass(d,t) for d,t in volumes),
    nodes=len(gmsh.model.mesh.getNodes()[0]),element_types=list(map(int,types)),tetra10=len(ids[0]),
    min_sicn=min(quality),size_mm=.8,seconds=time.perf_counter()-start,
    before_high_order_optimization=before_quality,nonpositive=sum(q<=0 for q in quality),
    source_model_unchanged=True,structural_solve=False)
(root/'clip-mesh-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
gmsh.finalize()
