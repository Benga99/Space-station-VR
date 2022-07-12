using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Globalization;

public class PositionsReaderCSV : MonoBehaviour
{
    public GameObject point;





    List<string> listA = new List<string>();
    List<Vector3> listV = new List<Vector3>();
    // Start is called before the first frame update
    void Start()
    {
        point.transform.localScale = new Vector3(0.015f, 0.015f, 0.015f);
        Read();

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
                listV.Add(StringToVector3(line));
            }
        }

        StartCoroutine(createTrace());
    }


    private IEnumerator createTrace()
    {
        foreach(var pos in listV)
        {
            Instantiate(point, pos, Quaternion.identity, this.transform);
            yield return new WaitForEndOfFrame();
            yield return new WaitForEndOfFrame();
            yield return new WaitForEndOfFrame();
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

        return result;
    }
}
