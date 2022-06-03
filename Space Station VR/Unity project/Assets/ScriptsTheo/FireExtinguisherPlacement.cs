using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR.InteractionSystem;

public class FireExtinguisherPlacement : MonoBehaviour
{
    [SerializeField]
    private GameObject FireExtinguisher;
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;
    [SerializeField]
    private Material startingMat;
    [SerializeField]
    private Material pizzaMat;

    private bool fireExtIntroduced = false;
    private Vector3 finalPosition = new Vector3(2.4f, 1.4f, 14.7f);
    private Vector3 finalRotation = new Vector3(270, 270, 0);

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(putFireExtInPlace());
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!fireExtIntroduced)
        {
            if (other.gameObject.tag == "Fire" && (rightHand.GetComponent<Hand>().currentAttachedObject == FireExtinguisher ||
                                                    leftHand.GetComponent<Hand>().currentAttachedObject == FireExtinguisher))
            {
                GameObject hand = GetTheHand(other.gameObject);

                hand.GetComponent<Hand>().DetachObject(FireExtinguisher);

                StartCoroutine(putFireExtInPlace());

                fireExtIntroduced = true;

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


    private IEnumerator putFireExtInPlace()
    {
        Vector3 localPos = FireExtinguisher.transform.position;
        Vector3 localRot = FireExtinguisher.transform.rotation.eulerAngles;
        float i = 0;

        while (i<=1)
        {
            FireExtinguisher.transform.position = Vector3.Lerp(localPos, finalPosition, i);
            Vector3 r = Vector3.Lerp(localRot, finalRotation, i);
            Debug.Log(r);
            FireExtinguisher.transform.rotation.eulerAngles.Set(r.x, r.y, r.z);
            i += 0.05f;
            yield return new WaitForEndOfFrame();
        }
        StartCoroutine(rotateFireExt());
    }

    private IEnumerator rotateFireExt()
    {
        float time = 0;
        float rotation = 1;
        while(time < 2.5f)
        {
            FireExtinguisher.transform.Rotate(0, 0, rotation);
            FireExtinguisher.GetComponent<MeshRenderer>().material.Lerp(startingMat, pizzaMat, time / 4f);
            if(rotation < 100)
            {
                rotation += 0.5f;
            }
            time += Time.deltaTime;
            yield return new WaitForEndOfFrame();
        }
        //time = 0;
        FireExtinguisher.GetComponent<MeshRenderer>().material = pizzaMat;
        while (time <= 5)
        {
            FireExtinguisher.transform.Rotate(0, 0, rotation);
            FireExtinguisher.GetComponent<Renderer>().material.Lerp(startingMat, pizzaMat, time / 4f);
            if (rotation > 0)
            {
                rotation -= 0.5f;
            }
            time += Time.deltaTime;
            yield return new WaitForEndOfFrame();
        }
    }
}
