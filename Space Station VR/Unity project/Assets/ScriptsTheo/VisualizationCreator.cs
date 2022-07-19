using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Globalization;

public class VisualizationCreator : MonoBehaviour
{
    public GameObject Heart;
    public List<string> posPaths;
    public List<string> ECGCleanPaths;
    public List<string> HeartRatePaths;


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
    int HeartRateIndex = 0, positionIndex = 0, visPassed = 0;
    float timerPos = 0, timerECG = 0;
    // Start is called before the first frame update
    void Start()
    {
        //openPositionFile0(posPaths[0], 0);
        openPositionFile1(posPaths[1], 1);
        //openPositionFile2(posPaths[2], 2);
        //openPositionFile3(posPaths[3], 3);

        //openECGCleanFile0(ECGCleanPaths[0], 0); 
        openECGCleanFile1(ECGCleanPaths[1], 1);
        //openECGCleanFile2(ECGCleanPaths[2], 2);
        //openECGCleanFile3(ECGCleanPaths[3], 3);

        //openHeartRateFile0(HeartRatePaths[0], 0);
        openHeartRateFile1(HeartRatePaths[1], 1);
        //openHeartRateFile2(HeartRatePaths[2], 2);
        //openHeartRateFile3(HeartRatePaths[3], 3);





    }

    // Update is called once per frame
    void Update()
    {
        
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
        var harD = getHeartDataList(id);

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
        StartCoroutine(CreateSingleHeartVisualization(id));
    }

    private void openHeartRateFile1(string path, int id)
    {
        var harD = getHeartDataList(id);
        Debug.Log("6");
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
 

        StartCoroutine(CreateSingleHeartVisualization(id));
    }

    private void openHeartRateFile2(string path, int id)
    {
        var harD = getHeartDataList(id);

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
        StartCoroutine(CreateSingleHeartVisualization(id));
    }

    private void openHeartRateFile3(string path, int id)
    {
        var harD = getHeartDataList(id);

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
        StartCoroutine(CreateSingleHeartVisualization(id));
    }

    private void openPositionFile0(string path, int id)
    {
        Vector3 lastPos = Vector3.zero;
        Vector3 currentPos = Vector3.zero;
        var posList = getPosDataList(id);
        using (var reader = new StreamReader($"./Assets/AnalizedDataPreStudy/Positions/{path}.csv"))
        {
            while (!reader.EndOfStream)
            {
                for(int i = 0; i < 10; i++)
                {
                    reader.ReadLine();
                }

                var file = reader.ReadLine();

                if(file == null) { break; }
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
        var posList = getPosDataList(id);
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
        var posList = getPosDataList(id);
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
        var posList = getPosDataList(id);
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
                        positionData3.Add(Vector3.Lerp(lastPos, currentPos, i / dist));
                    }
                }

                positionData3.Add(currentPos);
            }
        }
        readyPosition = true;
    }

    private IEnumerator CreateSingleHeartVisualization(int id)
    {
        Debug.Log("create id: " + id);
        GameObject go;

        var posD = getPosDataList(id);
        var harD = getHeartDataList(id);
        var ecgD = getECGDataList(id);

        while(readyECGClean == false || readyPosition == false)
        {
            yield return new WaitForEndOfFrame();
        }

        while(positionIndex < posD.Count)
        {
            timerECG += Time.deltaTime;
            timerPos += Time.deltaTime;
            while (timerECG >= harD[HeartRateIndex].Item1)
            {
                HeartRateIndex++;
                //positionIndex++;
            }
            if(timerPos >= 0.1f)
            {
                timerPos = 0f;
                if(visPassed == 3)
                {
                    go = Instantiate(Heart, posD[positionIndex], Quaternion.identity);
                    StartCoroutine(deleteHeart(go));
                    float value = ecgD[HeartRateIndex];
                    float lerpValue = Mathf.InverseLerp(40, 140, value);

                    float mult = Mathf.Lerp(1.1f, 2, lerpValue);
                    float inte = Mathf.Lerp(0.005f, 0.02f, lerpValue);

                    go.GetComponent<Pulse>().multiplier = mult;
                    go.GetComponent<Pulse>().intensity = inte;

                    visPassed = 0;
                }
                

                positionIndex++;
                visPassed++;
            }
            yield return new WaitForEndOfFrame();
        }
        
    }

    private IEnumerator deleteHeart(GameObject h)
    {
        var matt = h.GetComponent<SpriteRenderer>().material;
        matt.color = new Color(matt.color.r, matt.color.g, matt.color.b, 0f);

        while (matt.color.a < 0.31f)
        {
            matt.color = new Color(matt.color.r, matt.color.g, matt.color.b, matt.color.a + 0.001f);
            yield return new WaitForEndOfFrame();
        }
        yield return new WaitForSeconds(5);
        //h.SetActive(false);
        matt = h.GetComponent<SpriteRenderer>().material;
        while (matt.color.a > 0)
        {
            matt.color = new Color(matt.color.r, matt.color.g, matt.color.b, matt.color.a - 0.001f);
            yield return new WaitForEndOfFrame();
        }
        h.SetActive(false);
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

        return result;
    }


}
