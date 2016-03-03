import fbx
import sys

if __name__ == "__main__":
    try:
        import FbxCommon
        from fbx import *
    except ImportError:
        import platform
        msg = 'You need to copy the content in compatible subfolder under /lib/python<version> into your python install folder such as '
        if platform.system() == 'Windows' or platform.system() == 'Microsoft':
            msg += '"Python26/Lib/site-packages"'
        elif platform.system() == 'Linux':
            msg += '"/usr/local/lib/python2.6/site-packages"'
        elif platform.system() == 'Darwin':
            msg += '"/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages"'
        msg += ' folder.'
        print(msg)
        sys.exit(1)

    # print sys.argv[1]

    manager = fbx.FbxManager.Create()

    importer = fbx.FbxImporter.Create(manager, 'myImporter')

    status = importer.Initialize(sys.argv[1])

    if status == False:
        print "Can't find file."

    scene = fbx.FbxScene.Create(manager, 'myScene')

    importer.Import(scene)
    # importer.Destroy()

    rootNode = scene.GetRootNode()
    nodes = []
    nodes.append(scene.GetRootNode())

    # print rootNode.GetChildCount(True)
    #Find all deforming nodes ahead of time and pas to this script...actually that won't work.


    #Type position (0)
    # print geoNode.GetGeometry().GetDeformer(0).GetCache()

    #Type eRigid (0)
    #ELinkMode (0): eNormalize
    geoNode = rootNode.FindChild('sphere')
    # geoNode = rootNode.FindChild('pSphere4')
    geometry = geoNode.GetGeometry()
    print 'Deformer Type: {}'.format(geometry.GetDeformer(0).GetDeformerType())
    print 'Deformer Count: {}'.format(geometry.GetDeformerCount())
    print 'Vertex Cache Channel Type: {}'.format(geoNode.GetGeometry().GetDeformer(0).ECacheChannelType()) #0 - ePositions

    cache = geometry.GetDeformer(0).GetCache()
    print 'Cache: {}'.format(cache)
    print 'Cache Type: {}'.format(cache.EFileFormat())
    print 'Cache File Format: {}'.format(cache.GetCacheFileFormat()) #2 - eMayaCache
    print 'EMC File Count: {}'.format(cache.EMCFileCount()) #0 - eMCOneFile


    print 'File Open: {}'.format(cache.OpenFileForRead())
    print 'Channel Count: {}'.format(cache.GetChannelCount())
    print 'Channel Type: {}'.format(cache.GetChannelDataType(0)) #3 - eDoubleVectorArray double* [3]
    print 'Frame Number: {}'.format(cache.GetDataCount(0))
    fbxTime = FbxTime(1)
    fbxTime.SetFrame(1)
    print fbxTime.GetFrameCount()
    # print cache.Read(0, fbxTime, 1)
    # check, val = 'Channel Point Count: {}'.format(cache.GetChannelPointCount(0, fbxTime))
    initialPoints = cache.Read(0, fbxTime, 22202)
    # for i in range(0,len(initialPoints),3):
    #     print '{} {} {}'.format(initialPoints[i], initialPoints[i+1], initialPoints[i+2])

    fbxTime.SetFrame(48)
    finalPoints = cache.Read(0, fbxTime, 22202)
    geometry.RemoveDeformer(0)

    # for i in range(0,len(initialPoints),3):
    #     print '{} {} {}'.format(finalPoints[i], finalPoints[i+1], finalPoints[i+2])

    # print 'File Closed: {}'.format(cache.CloseFile())


    #BLEND SHAPE CONSTRUCTION
    # lBlendShape = FbxBlendShape.Create(scene,"HoudiniBlendShape")
    # lBlendShapeChannel01 = FbxBlendShapeChannel.Create(scene,"HoudiniBlend")

    #-------------PROBLEM AREA----------------
    #
    temp = geometry
    # #SETUP
    lBlendShape = FbxBlendShape.Create(temp, "HoudiniBlendShape")
    lBlendShape.SetGeometry(geometry)
    lBlendShapeChannel = FbxBlendShapeChannel.Create(temp, "HoudiniBlendShapeChannel")
    #
    #SHAPE 1
    lShape = FbxShape.Create(temp,"HoudiniBlend")
    lShape.InitControlPoints(len(initialPoints))
    print len(initialPoints)
    print '\nFrame 1'
    for i in range(0, len(initialPoints)/3):
            lShape.SetControlPointAt(FbxVector4(initialPoints[i*3], initialPoints[1+(i*3)], initialPoints[2+(i*3)], 1), i)
            print '{}:{}:{}:{}:{}'.format(initialPoints[i*3],initialPoints[1+(i*3)],initialPoints[2+(i*3)],1,i)

    lBlendShapeChannel.AddTargetShape(lShape,0)
    #
    # #SHAPE 2
    lShape = FbxShape.Create(temp, "HoudiniBlend")
    # lShape.InitControlPoints(len(finalPoints))
    print len(finalPoints)
    print '\nFrame 48'
    for i in range(0, len(finalPoints)/3):
            lShape.SetControlPointAt(fbx.FbxVector4(finalPoints[i*3], finalPoints[1+(i*3)], finalPoints[2+(i*3)], 1), i)
    #
    print lShape.GetControlPoints()
    #         # print '{}:{}:{}:{}:{}'.format(finalPoints[i*3],finalPoints[1+(i*3)],finalPoints[2+(i*3)],1,i)
    #
    #
    lBlendShapeChannel.AddTargetShape(lShape, 100)
    lBlendShape.AddBlendShapeChannel(lBlendShapeChannel)

    # lBlendShapeChannel.AddTargetShape(lShape)
    # geometry.AddDeformer(lBlendShape)
    print geometry.GetDeformerCount()
    # geometry.AddShape(0,0,lShapeTarget,100)

    #ADD DEFORMER
    # geometry.AddDeformer(lBlendShape)

    #CHECK

    # print geometry.GetDeformer(0).GetBlendShapeChannel(0).GetTargetShapeCount()
    # print geometry.GetDeformer(0).GetBlendShapeChannel(0).GetTargetShape(0).GetControlPoints()
    # print geometry.GetDeformer(0).GetBlendShapeChannel(0).GetTargetShape(1).GetControlPoints()
    # print geometry.GetDeformer(0).GetBlendShapeChannel(0).GetTargetShapeFullWeights()


    # geometry.SetDefaultShape(0,0,100)
    #-------------PROBLEM AREA^^^^----------------


    #ANIMATE
    lTime = FbxTime()
    lKeyIndex = 0

    # First animation stack.
    lAnimStackName = "Houdini test"
    lAnimStack = FbxAnimStack.Create(geoNode, lAnimStackName)

    # The animation nodes can only exist on AnimLayers therefore it is mandatory to
    # add at least one AnimLayer to the AnimStack. And for the purpose of this example,
    # one layer is all we need.
    lAnimLayer = FbxAnimLayer.Create(geoNode, "Base Layer")
    lAnimStack.AddMember(lAnimLayer)

    lGeoAttribute = geoNode.GetNodeAttribute()
    # The stretched shape is at index 0 because it was added first to the nurbs.
    lCurve = geometry.GetShapeChannel(0, 0, lAnimLayer, True)
    print lCurve
    if lCurve:
        lTime.SetFrame(1)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeyModifyBegin()
        lCurve.KeySetValue(lKeyIndex, 0.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)

        lTime.SetFrame(24)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeySetValue(lKeyIndex, 100.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)

        lTime.SetFrame(48)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeySetValue(lKeyIndex, 0.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
        lCurve.KeyModifyEnd()

    # The box shape is at index 1 because it was added second to the nurbs.
    # lCurve = lGeoAttribute.GetShapeChannel(0, 1, lAnimLayer, True)
    # if lCurve:
    #     lTime.SetFrame(1)
    #     lKeyIndex = lCurve.KeyAdd(lTime)[0]
    #     lCurve.KeyModifyBegin()
    #     lCurve.KeySetValue(lKeyIndex, 0.0)
    #     lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
    #
    #     lTime.SetFrame(48)
    #     lKeyIndex = lCurve.KeyAdd(lTime)[0]
    #     lCurve.KeySetValue(lKeyIndex, 100.0)
    #     lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
    #     lCurve.KeyModifyEnd()

    #We only need the first and last frame to create the blend shape

    ios = fbx.FbxIOSettings.Create(manager, IOSROOT)
    ios.SetBoolProp(EXP_FBX_MATERIAL, True)
    ios.SetBoolProp(EXP_FBX_TEXTURE, True)
    ios.SetBoolProp(EXP_FBX_ANIMATION, True)
    ios.SetBoolProp(EXP_FBX_SHAPE, True)

    lExporter = fbx.FbxExporter.Create(manager, "")

    lExporter.Initialize(sys.argv[2], -1, ios)

    # print 'test {}'.format(geometry.GetShape(0,0,0).GetControlPoints())
    # print 'test {}'.format(geometry.GetShape(0,0,1).GetControlPoints())

    lExporter.Export(scene)
    lExporter.Destroy()

    sys.exit(0)
