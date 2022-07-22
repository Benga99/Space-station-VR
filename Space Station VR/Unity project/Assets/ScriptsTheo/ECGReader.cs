using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class ECGReader : MonoBehaviour
{
    public LineRenderer line;

    //private List<float> ECGCleanData = new List<float>();

    //private List<(float, float)> HeartRateData = new List<(float, float)>();


    private Pulse pulse;
    private bool readyECGClean = false;

    // Start is called before the first frame update
    void Start()
    {
        pulse = GetComponent<Pulse>();
    }

    // Update is called once per frame
    void Update()
    {
        transform.LookAt(Camera.main.transform);
    }


    public IEnumerator lineFlow(List<float> ECGCleanData, List<(float, float)> HeartRateData)
    {
        Debug.Log("Line flow starting");
        float timerECG = 0;
        int index = 0, localIndex = 0;
        int size = 100;
        Vector3[] valuesList = new Vector3[size];
        line.positionCount = size;
        for(float i = -0.5f; i <= 2.7f; i += 0.025f)
        {
            if(localIndex < size)
            {
                valuesList[localIndex].x = i;
                valuesList[localIndex++].z = 0;
            }
            else
            {
                break;
            }
        }
        

        while (index < ECGCleanData.Count - size)
        {
            localIndex = 0;
            for(int i = index; i < index + size; i++)
            {
                valuesList[localIndex++].y = (ECGCleanData[i])/400f;
            }
            index++;
            while (timerECG >= HeartRateData[index].Item1)
            {
                index++;
            }
            line.SetPositions(valuesList);

            timerECG += Time.deltaTime;
            yield return new WaitForFixedUpdate();
        }
    }

}
