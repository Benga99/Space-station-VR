using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR.InteractionSystem;
using Valve.VR;

public class OpenMetalBoxScene4 : MonoBehaviour
{
    [SerializeField]
    private GameObject door;
    [SerializeField]
    private GameObject locker;
    [SerializeField]
    private GameObject metalKey;
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;

    private bool keyIntroduced = false;
    private InteractableFunctionality interFunc;

    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!keyIntroduced)
        {
            if (other.gameObject.tag == "MetalKey" && (rightHand.GetComponent<Hand>().currentAttachedObject == metalKey ||
                                                    leftHand.GetComponent<Hand>().currentAttachedObject == metalKey))
            {
                GameObject hand = GetTheHand(other.gameObject);

                hand.GetComponent<Hand>().DetachObject(metalKey);

                metalKey.SetActive(false);
                keyIntroduced = true;
                StartCoroutine(takeLockDown());
                //StartCoroutine(openBox());

            }
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

    private IEnumerator takeLockDown()
    {
        Transform lck = locker.transform.GetChild(2).transform;
        float pos = 0;
        while (pos < 0.006f)
        {
            lck.position = new Vector3(lck.position.x, lck.position.y + 0.0001f, lck.position.z);
            pos += 0.0001f;
            yield return new WaitForEndOfFrame();
        }
        float rotation = 0;
        while (rotation < 130)
        {
            lck.Rotate(0, 1f, 0);
            rotation += 1f;
            yield return new WaitForEndOfFrame();
        }
        interFunc.DeactivateRigidbodyConstraints(locker);
        locker.GetComponent<Rigidbody>().useGravity = true;
        StartCoroutine(openBox());
        yield return new WaitForSeconds(2);
        locker.GetComponent<Rigidbody>().useGravity = false;
        
    }

    private IEnumerator openBox()
    {
        Transform doorT = door.transform;
        float rotation = 0;
        while (rotation < 93)
        {
            doorT.Rotate(0, 0, 0.5f);
            rotation += 0.5f;
            yield return new WaitForEndOfFrame();
        }
    }
}
