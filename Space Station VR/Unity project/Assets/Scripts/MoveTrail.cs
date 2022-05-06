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
    float offset = 0;
    int length;
    Vector3[] posVector;
    Vector3[] nextPositionVector;
    Vector3[] interpolateVectors;
    // Start is called before the first frame update
    void Start()
    {
        Initialize();
        StartCoroutine(move());
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void Initialize()
    {
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
        Debug.Log(j);
    }

    private IEnumerator move()
    {
        this.transform.localPosition = interpolateVectors[i++];
        if (i == length)
        {
            StartCoroutine(kill());
               

            i = length - 1;
        }
        yield return new WaitForSeconds(0f);

        StartCoroutine(move());
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
            yield return new WaitForFixedUpdate();
        }
        yield return new WaitForSeconds(0f);
        Destroy(this.gameObject);
        StopAllCoroutines();
    }
}
