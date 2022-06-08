using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class ThreeDLine : MonoBehaviour
{
    public Hand leftHand, rightHand;
    public Transform pen;
    public Transform parentT;
    public GameObject circle;

    public LineRenderer lineR;

    public SteamVR_Action_Boolean touchPad;

    public SteamVR_Input_Sources inputSource = SteamVR_Input_Sources.Any;

    private List<Vector3> circles = new List<Vector3>();
    int i = 0, j = 0;

    private bool canDraw = false;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (touchPad.stateDown && (leftHand.currentAttachedObject == this.gameObject || rightHand.currentAttachedObject == this.gameObject) )
        {
            canDraw = !canDraw;
            if(canDraw == false)
            {
                circles.Clear();
                i = 0;
            }
        }
    }

    public void Writing()
    {
        if (canDraw)
        {
            GameObject c = Instantiate(circle, pen.position, pen.rotation);
            circles.Add(c.transform.position);
            if (circles.Count > 1)
            {
                if (Vector3.Distance(circles[i], circles[i - 1]) > 0.001f)
                {
                    StartCoroutine(spawnOtherCircles(circles[i], circles[i - 1]));
                }
            }
            i++;
        }
        
    }

    private IEnumerator spawnOtherCircles(Vector3 one, Vector3 two)
    {
        Debug.Log("in coroutine");
        for(float i = 0.2f; i <= 0.8f; i += 0.2f)
        {
            Instantiate(circle, Vector3.Lerp(one, two, i), Quaternion.identity);
        }
        yield return new WaitForEndOfFrame();
    }
    

    public void LineWriting()
    {
        Vector3[] positions = new Vector3[lineR.positionCount+11];
        var pos = positions[lineR.positionCount - 1];
        lineR.GetPositions(positions);

        for(int k = lineR.positionCount; k<=lineR.positionCount + 9; k++)
        {
            positions[k] = Vector3.Lerp(pos, pen.transform.position, (k-lineR.positionCount)/10f);
        }
        positions[lineR.positionCount + 10] = pen.transform.position;

        lineR.SetPositions(positions);
    }

    public void onRelease()
    {
        circles.Clear();
        i = 0;
        canDraw = false;
    }
}
