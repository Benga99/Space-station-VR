using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LightSpawnerV2 : MonoBehaviour
{
    [SerializeField]
    private GameObject lightPrefab;
    [SerializeField]
    private GameObject lightParent;
    [SerializeField]
    private GameObject emptyParent;

    public bool follow = true;

    GameObject obj;
    float minX = -20, maxX = 20;
    int i = 0;

    GameObject parent = null, child = null;
    float time = 0;
    bool once = false, broken = false;
    // Start is called before the first frame update
    void Start()
    {
        parent = this.gameObject;
        Application.targetFrameRate = 90;
        StartCoroutine(Spawn());
    }

    // Update is called once per frame
    void Update()
    {
        time += Time.deltaTime;
        if(time > 4.7f && !broken)
        {
            broken = true;
            //Debug.Break();
        }

        if(time > 5)
        {
            time = 0;
            
        }
    }

    private IEnumerator Spawn()
    {
        if(obj == null)
        {
            obj = Instantiate(lightPrefab, lightParent.transform);
        }
        else
        {
            obj = Instantiate(lightPrefab, obj.transform.localPosition + new Vector3(i, 0, 0), obj.transform.rotation, lightParent.transform);
            child = obj;
        }
        yield return new WaitForSeconds(1f);
        i++;
        //StartCoroutine(Spawn());
    }
}
