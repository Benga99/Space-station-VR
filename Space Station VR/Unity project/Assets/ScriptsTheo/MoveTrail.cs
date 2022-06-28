using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveTrail : MonoBehaviour
{
    [SerializeField]
    private Material newMat;
    [SerializeField]
    private List<Vector3> positions;


    int i = 0;
    int length;
    float offset = 0;
    Vector3 direction;
    Vector3[] posVector;
    Vector3[] nextPositionVector;
    public Vector3[] interpolateVectors;
    // Start is called before the first frame update
    void Start()
    {
        Initialize();
        StartCoroutine(move());
        //StartCoroutine(lineFlow());
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void Initialize()
    {
        //lightChild = gameObject.transform.GetChild(2).gameObject.GetComponent<Light>();

        for(var pos = 0;pos<positions.Count; pos++)
        {
            positions[pos] -= new Vector3(6.25f, 5.375f);
        }


        length = positions.Count;

        posVector = new Vector3[length];
        nextPositionVector = new Vector3[length];
        interpolateVectors = new Vector3[length * 20];

        for (int i = 0; i < length; i++)
        {
            posVector[i] = positions[i];
        }

        int j = 0;
        for (int i = 0; i < length-1; i++)
        {
            interpolateVectors[j++] = posVector[i];
            for (int k = 5; k <= 95; k += 5)
            {
                interpolateVectors[j++] = Vector3.Lerp(posVector[i], posVector[i + 1], k / 100f);
            }
        }
        length = j;
    }

    private IEnumerator move()
    {
        for (i = 0; i < length; i++)
        {
            if(i > 0)
            {
                direction = (interpolateVectors[i] - interpolateVectors[i - 1]).normalized;
            }
            
            this.transform.localPosition = interpolateVectors[i++]/* + new Vector3(offset, 0, 0)*/;
            
            yield return new WaitForSeconds(0.02f);
        }
        if (i == length)
        {
            //StartCoroutine(kill());
            offset = 0.6f;
            this.transform.parent.position -= direction * 0.6f;

            i = 0;
        }
        StartCoroutine(move());
    }

    private IEnumerator lineFlow()
    {
        Vector3 newPosition = interpolateVectors[0];
        for (int i = 0; i < length - 1; i++)
        {
            interpolateVectors[i].y = interpolateVectors[i + 1].y;
        }
        newPosition = new Vector3(interpolateVectors[length - 1].x, newPosition.y);
        interpolateVectors[length - 1] = newPosition;

        yield return new WaitForSeconds(0.2f);

        //TODO to adjust speed for the EKG to go faster
        //line.SetPositions(interpolateVectors);

        StartCoroutine(lineFlow());
    }

    private IEnumerator kill()
    {
        //var par = new Vector3(this.transform.parent.position.x, 0, 0);
        //var child = new Vector3(0, this.transform.position.y, this.transform.position.z);
        //this.transform.parent = null;
        //this.transform.position = par + child;
        while (this.gameObject.transform.localScale.x > 0f)
        {
            this.gameObject.transform.localScale -= new Vector3(0.0001f, 0.0001f, 0.0001f);
            //lightChild.intensity -= 0.002f;
            yield return new WaitForFixedUpdate();
        }
        yield return new WaitForSeconds(10f);
        Destroy(this.gameObject);
        StopAllCoroutines();
    }
}
