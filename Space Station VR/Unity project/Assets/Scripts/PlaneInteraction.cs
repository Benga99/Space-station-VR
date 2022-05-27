using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlaneInteraction : MonoBehaviour
{
    float timeSpent = 0f;
    bool messageSent = false;

    float initialPulse, offset;

    [SerializeField]
    private GameObject image;

    private Pulse[] pulses;

    private void Start()
    {
        pulses = FindObjectsOfType<Pulse>();
    }

    private void Update()
    {
        if(timeSpent > 2)
        {
            if (!messageSent)
            {
                Debug.Log("colided with " + this.gameObject.name);
                messageSent = true;
                //image.SetActive(true);
            }
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        
    }

    private void OnTriggerStay(Collider other)
    {
        timeSpent += Time.deltaTime;
    }

    private void OnTriggerExit(Collider other)
    {
        if (messageSent)
        {
            Debug.Log("Time spent on " + this.gameObject.name + ": " + timeSpent.ToString("0.00") + " seconds");
        }
        timeSpent = 0f;
        messageSent = false;   
    }
}
