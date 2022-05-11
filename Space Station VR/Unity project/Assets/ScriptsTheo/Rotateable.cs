using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Valve.VR;
using Valve.VR.InteractionSystem;


public class Rotateable : MonoBehaviour
{
    [SerializeField]
    private AudioSource numberAudio;
    [SerializeField]
    private AudioSource finalAudio;
    [SerializeField]
    private float timeToSolve = 1.5f;
    [SerializeField]
    private GameObject door;
    [SerializeField]
    private GameObject rotationObjectForSafe;

    private InteractableFunctionality interFunc;
    private Transform initialDoorTransform;

    float posX, posY, posZ;
    Vector3 pos;

    bool touched = false;
    bool doorOpened = true;

    private Hand currentHand;
    private float previousHandRot = 0f, actualHandRot = 0f, startHandRot = 0f;
    private float lastY = 0f;
    private int lastNumber = -2;
    private float timeSinceLastNumberChanged = 0f;
    private bool numberAdded = false;
    private List<int> CODE = new List<int>();
    public List<int> solution = new List<int>();
    private int solutionIndex = 0;

    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        initialDoorTransform = door.GetComponent<Transform>();

        posX = gameObject.transform.position.x;
        posY = gameObject.transform.position.y;
        posZ = gameObject.transform.position.z;
        pos = new Vector3(posX, posY, posZ);

        
        solution.Add(1);
        solution.Add(2);
        solution.Add(3);
        solution.Add(4);
        //StartCoroutine(OpenDoor());
    }

    // Update is called once per frame
    void Update()
    {
        if (touched)
        {
            float toRotateY = Mathf.Floor((actualHandRot) * 100) / 10f;
            this.gameObject.transform.Rotate(new Vector3(0, toRotateY, 0));

            CheckDuration(this.gameObject.transform.localRotation.eulerAngles.y);
        }
        if (doorOpened)
        {
            door.transform.position = initialDoorTransform.position;
        }
    }

    private void CheckDuration(float yRot)
    {
        int numb = getClockNumber(yRot);
        if (numb == lastNumber)
        {
            timeSinceLastNumberChanged += Time.deltaTime;
        }
        else
        {
            timeSinceLastNumberChanged = 0f;
            lastNumber = numb;
            numberAdded = false;
        }

        if(timeSinceLastNumberChanged > timeToSolve && numb != -1)
        {
            if (!numberAdded)
            {
                numberAdded = true;
                if(numb == solution[solutionIndex])
                {
                    if(solutionIndex != solution.Count - 1)
                    {
                        numberAudio.Play();
                    }
                    solutionIndex++;
                    Debug.Log("Found " + numb);

                    if(solutionIndex == solution.Count)
                    {
                        finalAudio.Play();
                        Debug.Log("riddle Complete");
                        touched = false;
                        interFunc.DeactivateRigidbodyConstraints(this.gameObject);
                        StartCoroutine(OpenDoor());
                        doorOpened = true;
                    }

                    CODE.Add(numb);
                }
                
            }
        }
    }

    private int getClockNumber(float y)
    {
        if (y < 345f && y >= 315f)
        {
            //Number 1
            return 1;
        }
        if (y < 315f && y >= 285f)
        {
            //Number 2
            return 2;
        }
        if (y < 285f && y >= 255f)
        {
            //Number 3
            return 3;
        }
        if (y < 255f && y >= 225f)
        {
            //Number 4
            return 4;
        }
        if (y < 225f && y >= 195f)
        {
            //Number 5
            return 5;
        }
        if (y < 195f && y >= 165f)
        {
            //Number 6
            return 6;
        }
        if (y < 165f && y >= 135f)
        {
            //Number 7
            return 7;
        }
        if (y < 135f && y >= 105f)
        {
            //Number 8
            return 8;
        }
        if (y < 105f && y >= 75f)
        {
            //Number 9
            return 9;
        }
        if (y < 75f && y >= 45f)
        {
            //Number 10
            return 10;
        }
        if (y < 45f && y >= 15f)
        {
            //Number 11
            return 11;
        }
        if (y < 15f || y >= 345f)
        {
            //Number 12
            return 12;
        }
        return -1;
        
    }

    public void setTouching(bool t)
    {
        touched = t;
    }

    protected virtual void OnAttachedToHand(Hand hand)
    {
        currentHand = hand;
        startHandRot = currentHand.transform.rotation.z;
        previousHandRot = startHandRot;
        actualHandRot = currentHand.transform.rotation.z;

        rotationObjectForSafe.SetActive(true);
        rotationObjectForSafe.transform.parent = hand.gameObject.transform;
        rotationObjectForSafe.transform.localPosition = Vector3.zero;
        rotationObjectForSafe.transform.localRotation = Quaternion.identity;
    }

    public void onUpdate()
    {
        actualHandRot = currentHand.transform.rotation.z - startHandRot;
    }

    public void OnDetachedHand()
    {
        StartCoroutine(decreaseActualHandRot());
    }

    private IEnumerator decreaseActualHandRot()
    {
        int act = 1;
        int pre = 1;
        if(actualHandRot < 0f)
        {
            act = -1;
        }
        if (previousHandRot < 0f)
        {
            pre = -1;
        }

        if(act == 1 && pre == 1)
        {
            while (Mathf.Abs(actualHandRot) > 0f || Mathf.Abs(previousHandRot) > 0f)
            {
                actualHandRot = Mathf.Clamp((actualHandRot - act*Time.deltaTime), 0, actualHandRot);
                previousHandRot = Mathf.Clamp((previousHandRot - pre*Time.deltaTime), 0, previousHandRot);

                yield return new WaitForEndOfFrame();
            }
        }
        else if(act == 1 && pre == -1)
        {
            while (Mathf.Abs(actualHandRot) > 0f || Mathf.Abs(previousHandRot) > 0f)
            {
                actualHandRot = Mathf.Clamp((actualHandRot - act * Time.deltaTime), 0, actualHandRot);
                previousHandRot = Mathf.Clamp((previousHandRot - pre * Time.deltaTime), previousHandRot, 0);

                yield return new WaitForEndOfFrame();
            }
        }
        else if (act == -1 && pre == 1)
        {
            while (Mathf.Abs(actualHandRot) > 0f || Mathf.Abs(previousHandRot) > 0f)
            {
                actualHandRot = Mathf.Clamp((actualHandRot - act * Time.deltaTime), actualHandRot, 0);
                previousHandRot = Mathf.Clamp((previousHandRot - pre * Time.deltaTime), 0, previousHandRot);

                yield return new WaitForEndOfFrame();
            }
        }
        else if (act == -1 && pre == -1)
        {
            while (Mathf.Abs(actualHandRot) > 0f || Mathf.Abs(previousHandRot) > 0f)
            {
                actualHandRot = Mathf.Clamp((actualHandRot - act * Time.deltaTime), actualHandRot, 0);
                previousHandRot = Mathf.Clamp((previousHandRot - pre * Time.deltaTime), previousHandRot, 0);

                yield return new WaitForEndOfFrame();
            }
        }       
    }

    private IEnumerator OpenDoor()
    {
        float multiplier = 20f;
        yield return new WaitForSeconds(1f);
        Debug.Log("openDoor");
        float degrees = 0;
        while(multiplier > 0f)
        {
            degrees += Time.deltaTime* multiplier;
            door.transform.Rotate(new Vector3(0, 0, -Time.deltaTime* multiplier));
            
            if(degrees > 5)
            {
                multiplier -= Time.deltaTime*15;
            }

            yield return new WaitForEndOfFrame();
        }
    }

}
