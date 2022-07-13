using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Collections;
using Unity.Jobs;

public class Pulse : MonoBehaviour
{
    [SerializeField]
    public float intensity = 0.01f;

    private bool coroutineAllowed = false;

    float maxX=0, maxY=0;
    public float multiplier = 3;
    public bool active = false;

    public Transform lookAt;

    // Start is called before the first frame update
    void Start()
    {
        coroutineAllowed = true;
        Debug.Log(this.gameObject.name);
    }

    // Update is called once per frame
    void Update()
    {
        if (coroutineAllowed)
        {
            maxX = 0;
            maxY = 0;
            StartCoroutine(Pulsing());
        }
        if (Vector3.Distance(transform.position, Camera.main.transform.position) > 0.4f)
        {
            if(lookAt == null)
            {
                transform.LookAt(Camera.main.transform);
            }
            else
            {
                transform.LookAt(lookAt);
                transform.Rotate(0, 180, 0);
            }
            
        }

    }

    private IEnumerator Pulsing()
    {
        coroutineAllowed = false;

        for(float i = 0; i < 1f; i += intensity)
        {
            Vector3 scale = new Vector3(
                Mathf.Lerp(transform.localScale.x, transform.localScale.x + intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                Mathf.Lerp(transform.localScale.y, transform.localScale.y + intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                transform.localScale.z
                );
            transform.localScale = scale;

            if(scale.x > maxX)
            {
                maxX = scale.x;
            }
            if (scale.y > maxY)
            {
                maxY = scale.y;
            }
            yield return new WaitForEndOfFrame();
        }

        for (float i = 0; i < 1f; i += intensity)
        {
            Vector3 scale = new Vector3(
                Mathf.Lerp(transform.localScale.x, transform.localScale.x - intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                Mathf.Lerp(transform.localScale.y, transform.localScale.y - intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                transform.localScale.z
                );
            transform.localScale = scale;
            yield return new WaitForEndOfFrame();
        }

        for (float i = 0; i < 1f; i += intensity)
        {
            Vector3 scale = new Vector3(
                Mathf.Lerp(transform.localScale.x, transform.localScale.x + intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                Mathf.Lerp(transform.localScale.y, transform.localScale.y + intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                transform.localScale.z
                );
            transform.localScale = scale;

            if (scale.x > maxX)
            {
                maxX = scale.x;
            }
            if (scale.y > maxY)
            {
                maxY = scale.y;
            }
            yield return new WaitForEndOfFrame();
        }

        for (float i = 0; i < 1f; i += intensity)
        {
            Vector3 scale = new Vector3(
                Mathf.Lerp(transform.localScale.x, transform.localScale.x - intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                Mathf.Lerp(transform.localScale.y, transform.localScale.y - intensity * intensity * multiplier, Mathf.SmoothStep(0f, 1f, i)),
                transform.localScale.z
                );
            transform.localScale = scale;
            yield return new WaitForEndOfFrame();
        }

        yield return new WaitForSeconds(1f/(intensity*100f));
        //Debug.Log(1f / (intensity * 200f));
        coroutineAllowed = true;
    }
}
