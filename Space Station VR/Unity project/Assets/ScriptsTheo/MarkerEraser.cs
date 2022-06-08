using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class MarkerEraser : MonoBehaviour
{
    public GameObject leftHand;
    public GameObject rightHand;
    public SteamVR_Action_Boolean touchPad;
    public List<float> scales;

    private bool pressed = false;
    private int i = 0;
    
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (touchPad.stateDown && !pressed && (rightHand.GetComponent<Hand>().currentAttachedObject == this.gameObject || leftHand.GetComponent<Hand>().currentAttachedObject == this.gameObject))
        {
            pressed = true;
            this.gameObject.transform.localScale = new Vector3(scales[i], scales[i], scales[i++]);
            if(i == 3) { i = 0; }
        }
        if (touchPad.stateUp)
        {
            pressed = false;
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if(other.gameObject.tag == "Sphere")
        {
            Destroy(other.gameObject);
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.tag == "Sphere")
        {
            Destroy(collision.gameObject);
        }
    }
}
