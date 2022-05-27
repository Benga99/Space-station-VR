using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Pulse : MonoBehaviour
{
    [SerializeField]
    public float intensity = 0.01f;

    private bool coroutineAllowed = false;

    float maxX=0, maxY=0;
    public float multiplier = 3;
    public bool active = false;

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
        /*
        if (Vector3.Distance(transform.position, Camera.main.transform.position) < 10)
        {
            active = true;
            float offset = intensity + 0.00001f;
            intensity = Mathf.Clamp(offset, 0.005f, 0.015f);
            multiplier = Mathf.Clamp(multiplier * (1 + offset / 30f), 3f, 6f);
        }
        else
        {
            active = false;
            float offset = intensity - 0.00001f;
            intensity = Mathf.Clamp(offset, 0.005f, 0.015f);
            multiplier = Mathf.Clamp(multiplier / (1 + offset / 20f), 3f, 6f);
        }
        */
        if (Vector3.Distance(transform.position, Camera.main.transform.position) > 0.4f)
        {
            transform.LookAt(Camera.main.transform);
            //transform.Rotate(transform.rotation.x / 3f, 180, 0);
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


        
        //Debug.Log($"maxX: {maxX}, maxY: {maxY}");
    }
}
