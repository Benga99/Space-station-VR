using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Valve.VR;
using Valve.VR.InteractionSystem;


public class Rotateable : MonoBehaviour
{
    float rotX, rotY, rotZ;
    float posX, posY, posZ;
    Vector3 pos;

    bool touching = false;

    private Hand currentHand;
    private float previousHandRot = 0f, actualHandRot = 0f;

    // Start is called before the first frame update
    void Start()
    {
        rotX = this.transform.rotation.x;
        rotY = this.transform.rotation.y;
        rotZ = this.transform.rotation.z;

        posX = this.transform.position.x;
        posY = this.transform.position.y;
        posZ = this.transform.position.z;
        pos = new Vector3(posX, posY, posZ);
    }

    // Update is called once per frame
    void Update()
    {
        //this.gameObject.transform.Rotate(new Vector3(0, 1, 0));
        if (touching)
        {
            float toRotateY = Mathf.Floor((-actualHandRot + previousHandRot) * 100) / 10f;
            //this.gameObject.transform.rotation = Quaternion.Euler(-90, this.gameObject.transform.rotation.y, 180);
            this.gameObject.transform.Rotate(new Vector3(0, toRotateY, 0));
            this.gameObject.transform.position = pos;
            //gameObject.GetComponent<Throwable>()
            Debug.Log(toRotateY);
        }
    }

    public void setTouching(bool t)
    {
        touching = t;
    }

    protected virtual void OnAttachedToHand(Hand hand)
    {
        currentHand = hand;
        previousHandRot = actualHandRot;
        actualHandRot = currentHand.transform.rotation.y;
        
        Debug.Log(hand.name);
    }

    public void onUpdate()
    {
        actualHandRot = currentHand.transform.rotation.y;
    }

    public void OnDetachedHand()
    {
        
    }
}
