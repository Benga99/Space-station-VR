using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR.InteractionSystem;
using Valve.VR;

public class Revolver : MonoBehaviour
{
    [SerializeField]
    private Vector3 muzzlePosition;
    [SerializeField]
    private ParticleSystem muzzleFlash;
    [SerializeField]
    private AudioSource audioShot;
    [SerializeField]
    private GameObject direction1;
    [SerializeField]
    private GameObject direction2;
    [SerializeField]
    private GameObject bullet;
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;
    [SerializeField]
    private SteamVR_Action_Boolean grabPinch;
    [SerializeField]
    private SteamVR_Action_Boolean TouchpadAction;
    [SerializeField]
    private SteamVR_Input_Sources inputSourceLeft;
    [SerializeField]
    private SteamVR_Input_Sources inputSourceRight;


    bool rightH = false;
    bool leftH = false;
    // Start is called before the first frame update
    void Start()
    {
        //TO DO TO TEST 
        leftHand.GetComponent<Hand>().grabPinchAction.AddOnStateUpListener(OnPinchUpLeft, inputSourceLeft);
        rightHand.GetComponent<Hand>().grabPinchAction.AddOnStateUpListener(OnPinchUpRight, inputSourceRight);

        leftHand.GetComponent<Hand>().grabPinchAction.AddOnStateDownListener(onPinchDownLeft, inputSourceLeft);
        rightHand.GetComponent<Hand>().grabPinchAction.AddOnStateDownListener(onPinchDownRight, inputSourceRight);
    }

    // Update is called once per frame
    void Update()
    {
        if(rightHand.GetComponent<Hand>().currentAttachedObject == this.gameObject)
        {
            rightH = true;
            leftH = false;
            if (TouchpadAction.stateDown)
            {
                rightHand.GetComponent<Hand>().DetachObject(this.gameObject);
            }
        }
        else if(leftHand.GetComponent<Hand>().currentAttachedObject == this.gameObject)
        {
            leftH = true;
            rightH = false;
            if (TouchpadAction.stateDown)
            {
                rightHand.GetComponent<Hand>().DetachObject(this.gameObject);
            }
        }
    }

    private void Fire()
    {
        muzzleFlash.Play();
        audioShot.Play();
        var pos = (direction2.transform.position - direction1.transform.position).normalized;
        GameObject bul = Instantiate(bullet, direction2.transform.position, this.transform.rotation);
        bul.transform.Rotate(90, 0, 0);
        StartCoroutine(moveBullet(bul, pos));

    }

    private IEnumerator moveBullet(GameObject bullet, Vector3 direction)
    {
        float time = 0;
        while(time < 10)
        {
            time += Time.deltaTime;
            bullet.transform.position += direction * Time.deltaTime * 10f;
            yield return new WaitForEndOfFrame();
        }

        Destroy(bullet);
    }

    private GameObject GetTheHand(GameObject card)
    {
        if (Vector3.Distance(card.transform.position, leftHand.transform.position) < Vector3.Distance(card.transform.position, rightHand.transform.position))
        {
            return leftHand;
        }
        else
        {
            return rightHand;
        }
    }

    private void OnPinchUpLeft(SteamVR_Action_Boolean action, SteamVR_Input_Sources input)
    {
        if (leftH == true)
        {
            leftH = false;
            leftHand.GetComponent<Hand>().AttachObject(this.gameObject, GrabTypes.Pinch);
        }
    }

    private void OnPinchUpRight(SteamVR_Action_Boolean action, SteamVR_Input_Sources input)
    {
        if (rightH == true)
        {
            rightH = false;
            rightHand.GetComponent<Hand>().AttachObject(this.gameObject, GrabTypes.Pinch);
        }
    }

    private void onPinchDownLeft(SteamVR_Action_Boolean action, SteamVR_Input_Sources input)
    {
        if(leftHand.GetComponent<Hand>().currentAttachedObject == this.gameObject)
        {
            Fire();
        }
    }

    private void onPinchDownRight(SteamVR_Action_Boolean action, SteamVR_Input_Sources input)
    {
        if (rightHand.GetComponent<Hand>().currentAttachedObject == this.gameObject)
        {
            Fire();
        }
    }
}
