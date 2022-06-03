using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class OperateSwitchButton : MonoBehaviour
{
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;
    [SerializeField]
    private Vector3 positionDown;
    [SerializeField]
    private Vector3 positionUp;

    private bool active = false;


    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!active)
        {
            if (rightHand.GetComponent<Hand>().currentAttachedObject == this.gameObject ||
                leftHand.GetComponent<Hand>().currentAttachedObject == this.gameObject)
            {
                GameObject hand = GetTheHand(other.gameObject);

                hand.GetComponent<Hand>().DetachObject(this.gameObject);
                Debug.Log("switchUp");
                active = !active;
                StartCoroutine(moveSwitchUp());
            }
        }
        else
        {
            if (rightHand.GetComponent<Hand>().currentAttachedObject == this.gameObject ||
                leftHand.GetComponent<Hand>().currentAttachedObject == this.gameObject)
            {
                GameObject hand = GetTheHand(other.gameObject);

                hand.GetComponent<Hand>().DetachObject(this.gameObject);
                Debug.Log("switchDown");
                active = !active;
                StartCoroutine(moveSwitchDown());
            }
        }
    }

    private IEnumerator moveSwitchUp()
    {
        float i = 0;
        while (i<=1)
        {
            this.gameObject.transform.localPosition = Vector3.Lerp(positionDown, positionUp, i);
            i += Time.deltaTime;
            yield return new WaitForEndOfFrame();
        }
    }

    private IEnumerator moveSwitchDown()
    {
        float i = 0;
        while (i <= 1)
        {
            this.gameObject.transform.localPosition = Vector3.Lerp(positionUp, positionDown, i);
            i += Time.deltaTime;
            yield return new WaitForEndOfFrame();
        }
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
}
