using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LightSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject lightPrefab;
    [SerializeField]
    private GameObject lightParent;
    [SerializeField][Range(1, 10)]
    private float SpawnFrequency;


    float minX = -20, maxX = 20;
    // Start is called before the first frame update
    void Start()
    {
        Application.targetFrameRate = 90;
        StartCoroutine(Spawn());
        var objs = FindObjectsOfType<LightSpawner>();
        foreach (var o in objs) 
        {
            Debug.Log(o.gameObject.name);
        }
    }

    // Update is called once per frame
    void Update()
    {
        transform.LookAt(Camera.main.transform);
        //transform.Rotate(0, 180, 0);
        //transform.localRotation.eulerAngles.Set(Mathf.Clamp(transform.localRotation.x, -20, 20), transform.localRotation.y, transform.localRotation.z);
        

        float rx = transform.eulerAngles.x;
        if(rx > 180)
        {
            rx = 360 - rx;
        }
        Debug.Log(rx);
        transform.Rotate(-rx + 15, 180, 0);
        //Debug.Log(transform.localRotation.eulerAngles.x);
    }

    private IEnumerator Spawn()
    {
        GameObject obj = Instantiate(lightPrefab, lightParent.transform);
        obj.transform.localScale = new Vector3(0f, 0, 0);
        while (obj.transform.localScale.x < 1f)
        {
            obj.transform.localScale += new Vector3(0.05f, 0.05f, 0.05f);
            yield return new WaitForFixedUpdate();
        }
        yield return new WaitForSeconds(SpawnFrequency);
        StartCoroutine(Spawn());
    }
}
