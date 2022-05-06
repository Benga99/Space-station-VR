using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LightSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject lightPrefab;
    [SerializeField]
    private GameObject lightParent;
    [SerializeField][Range(1, 5)]
    private float SpawnFrequency;
    // Start is called before the first frame update
    void Start()
    {
        Application.targetFrameRate = 90;
        StartCoroutine(Spawn());
    }

    // Update is called once per frame
    void Update()
    {
        
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
