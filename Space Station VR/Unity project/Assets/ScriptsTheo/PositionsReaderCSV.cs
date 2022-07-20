using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Globalization;

public class PositionsReaderCSV : MonoBehaviour
{
    public GameObject point;
    public GameObject canvas;

    public List<string> posPaths;
    public List<string> ECGCleanPaths;
    public List<string> HeartRatePaths;


    private List<Vector3> positionData0 = new List<Vector3>();
    private List<Vector3> positionData1 = new List<Vector3>();
    private List<Vector3> positionData2 = new List<Vector3>();
    private List<Vector3> positionData3 = new List<Vector3>();

    private List<(float, float)> HeartRateData0 = new List<(float, float)>();
    private List<(float, float)> HeartRateData1 = new List<(float, float)>();
    private List<(float, float)> HeartRateData2 = new List<(float, float)>();
    private List<(float, float)> HeartRateData3 = new List<(float, float)>();

    List<string> listA = new List<string>();
    List<Vector3> listV = new List<Vector3>();

    Vector3 prevPos = Vector3.zero, pos = Vector3.zero;
    int i = 0, offsetNumber = 13, index = 0;

    // Start is called before the first frame update
    void Start()
    {
        point.transform.localScale = new Vector3(0.015f, 0.015f, 0.015f);
        Read();
        //offsetNumber = positionsOffset.Count;
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void Read()
    {
        using (var reader = new StreamReader("./Assets/test-positions.csv"))
        {
            while (!reader.EndOfStream)
            {
                var line = reader.ReadLine();
                listA.Add(line);
                prevPos = pos;
                pos = StringToVector3(line);
                if (!prevPos.Equals(Vector3.zero) && !pos.Equals(Vector3.zero) && !prevPos.Equals(pos))
                {
                    if(index % offsetNumber == 6 || index % offsetNumber == 7)
                    {
                        for (float i = 0.1f; i <= 9.9f; i += 0.15f)
                        {
                            listV.Add(Vector3.Lerp(prevPos, pos, i / 10f));
                        }
                    }
                    else
                    {
                        for (float i = 0.5f; i <= 9.5f; i += 0.8f)
                        {
                            listV.Add(Vector3.Lerp(prevPos, pos, i / 10f));
                        }
                    }

                    
                }
                
                listV.Add(pos);
                index++;
            }
        }

        StartCoroutine(createTrace());
    }


    private IEnumerator createTrace()
    {
        Vector3 prevPos = Vector3.zero;
        foreach(var pos in listV)
        {
            Vector3 dir = (pos - prevPos).normalized;
            Vector3 actualDir = canvas.transform.forward;
            dir.y = 0;
            canvas.transform.position = pos;
            setForward(actualDir, dir);

            /*
            GameObject go = Instantiate(point, pos, Quaternion.identity, this.transform);
            StartCoroutine(deleteTrace(go));*/
            yield return new WaitForSeconds(0);
            prevPos = pos;
        }
    }

    private IEnumerator setForward(Vector3 actualDir, Vector3 dir)
    {
        float i = 0;
        while (i < 1)
        {
            canvas.transform.forward = Vector3.Lerp(actualDir, dir, i);
            i += Time.deltaTime*20;
            yield return new WaitForEndOfFrame();
        }
        
    }

    private IEnumerator deleteTrace(GameObject go)
    {
        yield return new WaitForSeconds(10);
        Destroy(go);
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
}
