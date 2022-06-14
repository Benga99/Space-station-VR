using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class DoorLvl5 : MonoBehaviour
{
    [SerializeField]
    private Hand leftHand;
    [SerializeField]
    private Hand rightHand;
    [SerializeField]
    private GameObject Soda;
    [SerializeField]
    private GameObject Key;
    [SerializeField]
    private GameObject SecondKey;
    [SerializeField]
    private Vector3 finalPosition;
    [SerializeField]
    private Vector3 finalRotation;


    private bool sodaIntroduced = false;


    private void OnTriggerEnter(Collider other)
    {
        if (!sodaIntroduced)
        {
            if (other.gameObject.tag == "Soda" && (rightHand.currentAttachedObject == Soda ||
                                                    leftHand.currentAttachedObject == Soda))
            {
                Hand hand = GetTheHand(other.gameObject);

                hand.DetachObject(Soda);
                other.gameObject.GetComponent<Rigidbody>().isKinematic = true;
                StartCoroutine(putSodaInPlace());

                sodaIntroduced = true;
            }
        }
    }

    private Hand GetTheHand(GameObject card)
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

    private IEnumerator putSodaInPlace()
    {
        Vector3 localPos = Soda.transform.position;
        float i = 0;

        while (i <= 1.5f)
        {
            Soda.transform.position = Vector3.Lerp(localPos, finalPosition, i);

            Vector3 r = Vector3.Lerp(finalRotation, finalRotation, i);

            Soda.transform.localEulerAngles = new Vector3(r.x, r.y, r.z);


            i += 0.05f;
            yield return new WaitForEndOfFrame();
        }
        StartCoroutine(rotateSoda());
    }

    private IEnumerator rotateSoda()
    {
        Key.SetActive(true);
        float time = 0;
        float rotation = 1;
        while (time < 4f)
        {
            Soda.transform.Rotate(0, 0, rotation);
            Key.transform.Rotate(0, rotation, 0);
            if(Soda.transform.localScale.z > 1.3f && Soda.transform.localScale.x > 0.01f)
            {
                Soda.transform.localScale = new Vector3(Soda.transform.localScale.x * 0.99f, Soda.transform.localScale.y * 0.99f, Soda.transform.localScale.z * 0.999f);
            }
            else if(Soda.transform.localScale.x > 0.01f) 
            {
                Soda.transform.localScale = new Vector3(Soda.transform.localScale.x * 0.99f, Soda.transform.localScale.y * 0.99f, Soda.transform.localScale.z);
            }

            if (rotation < 100)
            {
                rotation += 0.5f;
            }
            time += Time.deltaTime;
            yield return new WaitForEndOfFrame();
        }
        Soda.SetActive(false);
        
        while(rightHand.currentAttachedObject != Key && leftHand.currentAttachedObject != Key)
        {
            yield return new WaitForEndOfFrame();
        }
        yield return new WaitForSeconds(2f);
        SecondKey.SetActive(true);
    }
}
