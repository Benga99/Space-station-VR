using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class EKG : MonoBehaviour
{
    [SerializeField]
    private LineRenderer line;
    [SerializeField][Range(0, 0.05f)]
    private float speed = 0.05f;
    [SerializeField]
    private Text heartRateText;
    [SerializeField][Range(60, 150)]
    private int heartRateNumber;

    [SerializeField]
    private GameObject heart;

    private Pulse pulse;
    //GameObject -> Heart.transform.position = Camera.main.WorldToScreenPoint(line.gamobject.transform.position);
    float offset = 0;
    int length;
    Vector3[] posVector;
    Vector3[] nextPositionVector;
    Vector3[] interpolateVectors;

    // Start is called before the first frame update
    void Start()
    {
        pulse = this.gameObject.GetComponent<Pulse>();
        heartRateText.text = heartRateNumber.ToString() + " bpm";
        Initialize();
        StartCoroutine(lineFlow());
    }

    // Update is called once per frame
    void Update()
    {
        if(Vector3.Distance(transform.position, Camera.main.transform.position) < 10)
        {
            pulse.active = true;
            offset = pulse.intensity + 0.00001f;
            pulse.intensity = Mathf.Clamp(offset, 0.005f, 0.015f);
            pulse.multiplier = Mathf.Clamp(pulse.multiplier * (1 + offset / 30f), 3f, 6f);
        }
        else
        {
            pulse.active = false;
            offset = pulse.intensity - 0.00001f;
            pulse.intensity = Mathf.Clamp(offset, 0.005f, 0.015f);
            pulse.multiplier = Mathf.Clamp(pulse.multiplier / (1 + offset / 20f), 3f, 6f);
        }

        if(Vector3.Distance(transform.position, Camera.main.transform.position) > 0.4f)
        {
            transform.LookAt(Camera.main.transform);
            transform.Rotate(transform.rotation.x/3f, 180, 0);
        }
        
    }

    private void Initialize()
    {
        length = line.positionCount;

        posVector = new Vector3[length];
        nextPositionVector = new Vector3[length];
        interpolateVectors = new Vector3[length * 4];

        for (int i = 0; i < 14; i++)
        {
            posVector[i] = line.GetPosition(i);
        }
        
        int j = 0;
        for (int i = 0; i < 13; i++)
        {
            interpolateVectors[j++] = posVector[i];
            for (int k = 20; k <= 80; k += 20)
            {
                interpolateVectors[j++] = Vector3.Lerp(posVector[i], posVector[i + 1], k / 100f);
            }
        }
        line.SetPositions(interpolateVectors);
        length = j;
        Debug.Log(j);
    }


    private IEnumerator lineFlow()
    {
        Vector3 newPosition = interpolateVectors[0];
        for(int i = 0; i < length-1; i++)
        {
            interpolateVectors[i].y = interpolateVectors[i + 1].y;
        }
        newPosition = new Vector3(interpolateVectors[length - 1].x, newPosition.y);
        interpolateVectors[length - 1] = newPosition;

        yield return new WaitForSeconds(speed);

        //TODO to adjust speed for the EKG to go faster
        line.SetPositions(interpolateVectors);

        StartCoroutine(lineFlow());
    }
}
