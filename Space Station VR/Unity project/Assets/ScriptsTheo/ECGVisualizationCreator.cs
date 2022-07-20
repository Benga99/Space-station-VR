using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Globalization;

public class ECGVisualizationCreator : MonoBehaviour
{

    public GameObject ECG;

    public List<string> posPaths;
    public List<string> ECGCleanPaths;
    public List<string> HeartRatePaths;

    public bool vis0, vis1, vis2, vis3;

    private List<Vector3> positionData0 = new List<Vector3>();
    private List<Vector3> positionData1 = new List<Vector3>();
    private List<Vector3> positionData2 = new List<Vector3>();
    private List<Vector3> positionData3 = new List<Vector3>();

    private List<float> ECGCleanData0 = new List<float>();
    private List<float> ECGCleanData1 = new List<float>();
    private List<float> ECGCleanData2 = new List<float>();
    private List<float> ECGCleanData3 = new List<float>();


    private List<(float, float)> HeartRateData0 = new List<(float, float)>();
    private List<(float, float)> HeartRateData1 = new List<(float, float)>();
    private List<(float, float)> HeartRateData2 = new List<(float, float)>();
    private List<(float, float)> HeartRateData3 = new List<(float, float)>();

    bool readyPosition = false, readyECGClean = false;


    // Start is called before the first frame update
    void Start()
    {
        if (vis0)
        {
            openPositionFile0(posPaths[0], 0);
            openECGCleanFile0(ECGCleanPaths[0], 0);
            openHeartRateFile0(HeartRatePaths[0], 0);
            
        }
        if (vis1)
        {
            openPositionFile1(posPaths[1], 1);
            openECGCleanFile1(ECGCleanPaths[1], 1);
            openHeartRateFile1(HeartRatePaths[1], 1);
        }
        if (vis2)
        {
            openPositionFile2(posPaths[2], 2);
            openECGCleanFile2(ECGCleanPaths[2], 2);
            openHeartRateFile2(HeartRatePaths[2], 2);
        }
        if (vis3)
        {
            openPositionFile3(posPaths[3], 3);
            openECGCleanFile3(ECGCleanPaths[3], 3);
            openHeartRateFile3(HeartRatePaths[3], 3);
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    private void openPositionFile0(string path, int id)
    {
        Vector3 lastPos = Vector3.zero;
        Vector3 currentPos = Vector3.zero;
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Positions/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                for (int i = 0; i < 10; i++)
                {
                    reader.ReadLine();
                }

                var file = reader.ReadLine();

                if (file == null) { break; }
                lastPos = currentPos;
                currentPos = StringToVector3(file);

                if (lastPos != Vector3.zero)
                {
                    float dist = Vector3.Distance(lastPos, currentPos) * 30;
                    for (int i = 1; i < dist; i++)
                    {
                        positionData0.Add(Vector3.Lerp(lastPos, currentPos, i / dist));
                    }
                }

                positionData0.Add(currentPos);
            }
        }
        readyPosition = true;
    }

    private void openPositionFile1(string path, int id)
    {
        Vector3 lastPos = Vector3.zero;
        Vector3 currentPos = Vector3.zero;

        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Positions/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                for (int i = 0; i < 10; i++)
                {
                    if (!reader.EndOfStream)
                    {
                        reader.ReadLine();
                    }
                    else
                    {
                        break;
                    }
                }

                var file = reader.ReadLine();

                if (file == null) { break; }
                lastPos = currentPos;
                currentPos = StringToVector3(file);

                if (lastPos != Vector3.zero)
                {
                    float dist = Vector3.Distance(lastPos, currentPos) * 30;
                    for (int i = 1; i < dist; i++)
                    {
                        positionData1.Add(Vector3.Lerp(lastPos, currentPos, i / dist));
                    }
                }

                positionData1.Add(currentPos);
            }
        }
        readyPosition = true;
    }

    private void openPositionFile2(string path, int id)
    {
        Vector3 lastPos = Vector3.zero;
        Vector3 currentPos = Vector3.zero;

        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Positions/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                for (int i = 0; i < 10; i++)
                {
                    if (!reader.EndOfStream)
                    {
                        reader.ReadLine();
                    }
                    else
                    {
                        break;
                    }
                }

                var file = reader.ReadLine();

                if (file == null) { break; }
                lastPos = currentPos;
                currentPos = StringToVector3(file);

                if (lastPos != Vector3.zero)
                {
                    float dist = Vector3.Distance(lastPos, currentPos) * 30;
                    for (int i = 1; i < dist; i++)
                    {
                        positionData2.Add(Vector3.Lerp(lastPos, currentPos, i / dist));
                    }
                }

                positionData2.Add(currentPos);
            }
        }
        readyPosition = true;
    }

    private void openPositionFile3(string path, int id)
    {
        Vector3 lastPos = Vector3.zero;
        Vector3 currentPos = Vector3.zero;

        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Positions/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                for (int i = 0; i < 10; i++)
                {
                    if (!reader.EndOfStream)
                    {
                        reader.ReadLine();
                    }
                    else
                    {
                        break;
                    }
                    
                }

                var file = reader.ReadLine();

                if (file == null) { break; }
                lastPos = currentPos;
                currentPos = StringToVector3(file);

                if (lastPos != Vector3.zero)
                {
                    float dist = Vector3.Distance(lastPos, currentPos) * 30;
                    for (int i = 1; i < dist; i++)
                    {
                        positionData3.Add(Vector3.Lerp(lastPos, currentPos, i / dist));
                    }
                }

                positionData3.Add(currentPos);
            }
        }
        readyPosition = true;
    }


    // 1 value
    private void openECGCleanFile0(string path, int id)
    {
        var ecgD = getECGDataList(id);
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                ECGCleanData0.Add(float.Parse(line));
            }
        }
        readyECGClean = true;
    }

    private void openECGCleanFile1(string path, int id)
    {
        var ecgD = getECGDataList(id);
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                ECGCleanData1.Add(float.Parse(line));
            }
        }
        readyECGClean = true;
    }

    private void openECGCleanFile2(string path, int id)
    {
        var ecgD = getECGDataList(id);
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                ECGCleanData2.Add(float.Parse(line));
            }
        }
        readyECGClean = true;
    }

    private void openECGCleanFile3(string path, int id)
    {
        var ecgD = getECGDataList(id);
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                ECGCleanData3.Add(float.Parse(line));
            }
        }
        readyECGClean = true;
    }


    // 2 values
    private void openHeartRateFile0(string path, int id)
    {
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                var spl = line.Split(';');

                HeartRateData0.Add((float.Parse(spl[0]), float.Parse(spl[1])));

                reader.ReadLine();
            }
        }
        StartCoroutine(createTrace(id));
    }

    private void openHeartRateFile1(string path, int id)
    {
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                var spl = line.Split(';');

                HeartRateData1.Add((float.Parse(spl[0]), float.Parse(spl[1])));

                reader.ReadLine();
            }
        }
        StartCoroutine(createTrace(id));
    }

    private void openHeartRateFile2(string path, int id)
    {
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                var spl = line.Split(';');

                HeartRateData2.Add((float.Parse(spl[0]), float.Parse(spl[1])));

                reader.ReadLine();
            }
        }
        StartCoroutine(createTrace(id));
    }

    private void openHeartRateFile3(string path, int id)
    {
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Heart/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                var spl = line.Split(';');

                HeartRateData3.Add((float.Parse(spl[0]), float.Parse(spl[1])));

                reader.ReadLine();
            }
        }
        StartCoroutine(createTrace(id));
    }

    private IEnumerator createTrace(int id)
    {
        GameObject localECG = Instantiate(ECG);
        float timerECG = 0, timerPos = 0;
        Vector3 prevPos = Vector3.zero, pos = Vector3.zero;
        int HeartRateIndex = 0, positionIndex = 0, visPassed = 0;
        Debug.Log("create trace: " + id);

        var posD = getPosDataList(id);
        var harD = getHeartDataList(id);
        var ecgD = getECGDataList(id);

        StartCoroutine(localECG.GetComponent<ECGReader>().lineFlow(ecgD, harD));

        while (readyPosition == false)
        {
            yield return new WaitForEndOfFrame();
        }

        while (positionIndex < posD.Count)
        {
            pos = posD[positionIndex];


            timerECG += Time.deltaTime;
            timerPos += Time.deltaTime;
            while (timerECG >= harD[HeartRateIndex].Item1)
            {
                HeartRateIndex++;
                //positionIndex++;
            }
            if (timerPos >= 0.1f)
            {
                timerPos = 0f;
                if (visPassed == 1)
                {
                    Vector3 dir = (pos - prevPos).normalized;
                    Vector3 actualDir = localECG.transform.forward;
                    dir.y = 0;
                    localECG.transform.LeanMove(pos, 0.1f);
                    //ECG.transform.position = pos;
                    //setForward(actualDir, dir);
                    yield return new WaitForSeconds(0);
                    prevPos = pos;

                    visPassed = 0;
                }


                positionIndex++;
                visPassed++;
            }
            yield return new WaitForFixedUpdate();
        }
    }

    private IEnumerator setForward(Vector3 actualDir, Vector3 dir)
    {
        float i = 0;
        while (i < 1)
        {
            ECG.transform.forward = Vector3.Lerp(actualDir, dir, i);
            i += Time.deltaTime * 20;
            yield return new WaitForEndOfFrame();
        }

    }

    private Vector3 StringToVector3(string sVector)
    {
        // Remove the parentheses
        if (sVector.StartsWith("(") && sVector.EndsWith(")"))
        {
            sVector = sVector.Substring(1, sVector.Length - 2);
        }

        // split the items
        string[] sArray = sVector.Split(',');

        // store as a Vector3
        Vector3 result = new Vector3(
            float.Parse(sArray[0], CultureInfo.InvariantCulture.NumberFormat),
            float.Parse(sArray[1], CultureInfo.InvariantCulture.NumberFormat),
            float.Parse(sArray[2], CultureInfo.InvariantCulture.NumberFormat));

        return result/* + positionsOffset[(i++) % offsetNumber]*/;
    }


    private List<Vector3> getPosDataList(int id)
    {
        switch (id)
        {
            case 0:
                return positionData0;
            case 1:
                return positionData1;
            case 2:
                return positionData2;
            case 3:
                return positionData3;
            default:
                return null;
        }
    }

    private List<(float, float)> getHeartDataList(int id)
    {
        switch (id)
        {
            case 0:
                return HeartRateData0;
            case 1:
                return HeartRateData1;
            case 2:
                return HeartRateData2;
            case 3:
                return HeartRateData3;
            default:
                return null;
        }
    }


    private List<float> getECGDataList(int id)
    {
        switch (id)
        {
            case 0:
                return ECGCleanData0;
            case 1:
                return ECGCleanData1;
            case 2:
                return ECGCleanData2;
            case 3:
                return ECGCleanData3;
            default:
                return null;
        }
    }



}
